#!/usr/bin/env python3
"""
Santa Route Planner
Optimizes Santa's delivery route considering sleigh capacity constraints
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict
import json
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2


class SantaPlanner:
    def __init__(self, excel_file: str):
        """Initialize the Santa Planner with data from Excel file"""
        self.excel_file = excel_file
        self.load_data()

    def load_data(self):
        """Load all data from Excel sheets"""
        # Load children data
        self.children = pd.read_excel(self.excel_file, sheet_name='Sample Input')

        # Load articles data
        self.articles = pd.read_excel(self.excel_file, sheet_name='Articles')

        # Load slay metadata
        meta_df = pd.read_excel(self.excel_file, sheet_name='Slay Meta Data')
        self.max_weight = meta_df[meta_df['meta data'] == 'maximum weight']['value'].values[0]
        self.max_volume = meta_df[meta_df['meta data'] == 'maximum volume']['value'].values[0]
        self.speed_kmh = meta_df[meta_df['meta data'] == 'speed (km/h)']['value'].values[0]
        self.time_per_stop_min = meta_df[meta_df['meta data'] == 'time per stop (min)']['value'].values[0]

        # North Pole coordinates
        self.north_pole = (90.0, 0.0)

        # Filter out naughty children
        self.good_children = self.children[self.children['naughty'] == 0].copy()

        print(f"Loaded {len(self.children)} children ({len(self.good_children)} good, {len(self.children) - len(self.good_children)} naughty)")
        print(f"Sleigh capacity: {self.max_weight}kg, {self.max_volume} volume units")

    def haversine_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate the great circle distance between two points on Earth (in km)
        coord format: (latitude, longitude)
        """
        lat1, lon1 = radians(coord1[0]), radians(coord1[1])
        lat2, lon2 = radians(coord2[0]), radians(coord2[1])

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        # Earth's radius in km
        radius = 6371

        return radius * c

    def get_article_info(self, article_id: int) -> Tuple[float, float]:
        """Get weight and volume for an article"""
        article_row = self.articles[self.articles['article'] == article_id]
        if len(article_row) == 0:
            return 0.0, 0.0
        return article_row['weight'].values[0], article_row['volume'].values[0]

    def calculate_load_requirements(self, children_subset: pd.DataFrame) -> Dict[int, int]:
        """Calculate how many of each article we need for a subset of children"""
        wish_counts = children_subset['wish'].value_counts().to_dict()
        return wish_counts

    def can_fit_in_sleigh(self, article_counts: Dict[int, int]) -> bool:
        """Check if the given articles can fit in the sleigh"""
        total_weight = 0
        total_volume = 0

        for article_id, count in article_counts.items():
            weight, volume = self.get_article_info(article_id)
            total_weight += weight * count
            total_volume += volume * count

        return total_weight <= self.max_weight and total_volume <= self.max_volume

    def nearest_neighbor_from_point(self, start_coord: Tuple[float, float],
                                   remaining_children: pd.DataFrame) -> pd.DataFrame:
        """
        Use nearest neighbor heuristic to order children starting from a point
        """
        if len(remaining_children) == 0:
            return pd.DataFrame()

        ordered = []
        current_coord = start_coord
        remaining = remaining_children.copy()

        while len(remaining) > 0:
            # Calculate distances to all remaining children
            distances = remaining.apply(
                lambda row: self.haversine_distance(current_coord, (row['latitude'], row['longitude'])),
                axis=1
            )

            # Find nearest child
            nearest_idx = distances.idxmin()
            nearest_child = remaining.loc[nearest_idx]

            ordered.append(nearest_child)
            current_coord = (nearest_child['latitude'], nearest_child['longitude'])
            remaining = remaining.drop(nearest_idx)

        return pd.DataFrame(ordered)

    def greedy_cluster_by_capacity(self) -> List[pd.DataFrame]:
        """
        Cluster children into trips based on sleigh capacity using greedy approach
        """
        remaining = self.good_children.copy()
        trips = []

        while len(remaining) > 0:
            # Start a new trip from North Pole
            current_trip = pd.DataFrame()
            current_coord = self.north_pole
            trip_remaining = remaining.copy()

            # Try to add children to this trip using nearest neighbor
            while len(trip_remaining) > 0:
                # Calculate distances to all remaining children
                distances = trip_remaining.apply(
                    lambda row: self.haversine_distance(current_coord, (row['latitude'], row['longitude'])),
                    axis=1
                )

                # Sort by distance
                sorted_indices = distances.sort_values().index

                # Try to add the nearest children that fit in capacity
                added_any = False
                for idx in sorted_indices:
                    test_trip = pd.concat([current_trip, trip_remaining.loc[[idx]]])
                    article_counts = self.calculate_load_requirements(test_trip)

                    if self.can_fit_in_sleigh(article_counts):
                        # Add this child
                        current_trip = test_trip
                        current_coord = (trip_remaining.loc[idx, 'latitude'],
                                       trip_remaining.loc[idx, 'longitude'])
                        trip_remaining = trip_remaining.drop(idx)
                        added_any = True
                        break

                if not added_any:
                    # Can't add any more children to this trip
                    break

            # Save this trip
            if len(current_trip) > 0:
                trips.append(current_trip)
                remaining = remaining.drop(current_trip.index)

        return trips

    def optimize_trip_route(self, trip: pd.DataFrame) -> pd.DataFrame:
        """
        Optimize the route within a single trip using nearest neighbor
        """
        return self.nearest_neighbor_from_point(self.north_pole, trip)

    def generate_route_plan(self) -> List[Dict]:
        """
        Generate the complete route plan with refill stops
        """
        trips = self.greedy_cluster_by_capacity()

        print(f"\nGenerated {len(trips)} trips to deliver to {len(self.good_children)} children")

        route_plan = []

        for trip_num, trip in enumerate(trips, 1):
            # Calculate required articles for this trip
            article_counts = self.calculate_load_requirements(trip)

            # Add refill instructions
            for article_id, count in sorted(article_counts.items()):
                route_plan.append({
                    'stop': 0,
                    'article': float(article_id),
                    'pieces': float(count)
                })

            # Optimize route for this trip
            optimized_trip = self.optimize_trip_route(trip)

            # Add delivery stops
            for _, child in optimized_trip.iterrows():
                route_plan.append({
                    'stop': int(child['child']),
                    'article': None,
                    'pieces': None
                })

        return route_plan

    def calculate_total_distance(self, route_plan: List[Dict]) -> float:
        """Calculate total distance traveled"""
        total_distance = 0
        current_coord = self.north_pole

        for stop in route_plan:
            if stop['stop'] == 0:
                # Refill at North Pole - already here or need to return
                if current_coord != self.north_pole:
                    total_distance += self.haversine_distance(current_coord, self.north_pole)
                    current_coord = self.north_pole
            else:
                # Delivery stop
                child = self.good_children[self.good_children['child'] == stop['stop']].iloc[0]
                child_coord = (child['latitude'], child['longitude'])
                total_distance += self.haversine_distance(current_coord, child_coord)
                current_coord = child_coord

        # Return to North Pole
        total_distance += self.haversine_distance(current_coord, self.north_pole)

        return total_distance

    def calculate_total_time(self, route_plan: List[Dict]) -> float:
        """Calculate total time in hours"""
        distance = self.calculate_total_distance(route_plan)
        travel_time_hours = distance / self.speed_kmh

        # Count delivery stops (not refills)
        delivery_stops = sum(1 for stop in route_plan if stop['stop'] != 0)
        stop_time_hours = (delivery_stops * self.time_per_stop_min) / 60

        return travel_time_hours + stop_time_hours

    def save_route_to_csv(self, route_plan: List[Dict], output_file: str):
        """Save route plan to CSV with semicolon separator and comma as decimal"""
        df = pd.DataFrame(route_plan)

        # Replace NaN with empty string for proper CSV formatting
        df = df.fillna('')

        # Save with semicolon separator and comma as decimal
        df.to_csv(output_file, sep=';', decimal=',', index=False, float_format='%.1f')

        print(f"\nRoute plan saved to: {output_file}")

    def save_statistics(self, route_plan: List[Dict], output_file: str):
        """Save statistics for the dashboard"""
        stats = {
            'total_children': int(len(self.children)),
            'good_children': int(len(self.good_children)),
            'naughty_children': int(len(self.children) - len(self.good_children)),
            'total_stops': len([s for s in route_plan if s['stop'] != 0]),
            'total_refills': len([s for s in route_plan if s['stop'] == 0]),
            'total_distance_km': round(self.calculate_total_distance(route_plan), 2),
            'total_time_hours': round(self.calculate_total_time(route_plan), 2),
            'max_weight': float(self.max_weight),
            'max_volume': float(self.max_volume),
            'speed_kmh': float(self.speed_kmh),
            'generated_at': datetime.now().isoformat()
        }

        with open(output_file, 'w') as f:
            json.dump(stats, f, indent=2)

        print(f"Statistics saved to: {output_file}")
        print(f"\n{'='*60}")
        print(f"ROUTE STATISTICS")
        print(f"{'='*60}")
        print(f"Total children: {stats['total_children']}")
        print(f"Good children to deliver to: {stats['good_children']}")
        print(f"Naughty children (no delivery): {stats['naughty_children']}")
        print(f"Total delivery stops: {stats['total_stops']}")
        print(f"Total refill stops: {stats['total_refills']}")
        print(f"Total distance: {stats['total_distance_km']:.2f} km")
        print(f"Total time: {stats['total_time_hours']:.2f} hours")
        print(f"{'='*60}")


def main():
    """Main entry point"""
    print("Santa Route Planner")
    print("=" * 60)

    # Initialize planner
    planner = SantaPlanner('/home/user/Test/Kopie von Santa Planner.xlsx')

    # Generate route plan
    print("\nGenerating optimal route plan...")
    route_plan = planner.generate_route_plan()

    # Save to CSV
    planner.save_route_to_csv(route_plan, 'santa_route.csv')

    # Save statistics
    planner.save_statistics(route_plan, 'statistics.json')

    # Also save route plan as JSON for dashboard
    with open('route_plan.json', 'w') as f:
        json.dump(route_plan, f, indent=2)
    print("Route plan JSON saved to: route_plan.json")

    # Save children data as JSON for dashboard
    children_data = planner.children.to_dict('records')
    with open('children_data.json', 'w') as f:
        json.dump(children_data, f, indent=2)
    print("Children data saved to: children_data.json")


if __name__ == '__main__':
    main()
