"""Performance tests for the accessor library."""

import time
import unittest
from accessor import accessor as _


class TestPerformance(unittest.TestCase):
    """Test performance characteristics of the accessor library."""

    def setUp(self):
        """Set up test data."""
        # Create test data with deep nesting
        self.deep_data = {}
        current = self.deep_data
        for i in range(5):  # Reduced depth for testing
            current['level'] = {}
            current = current['level']
        current['value'] = 'deep_value'
        
        # Create large list data
        self.large_list_data = {
            'items': [{'id': i, 'value': i * 2} for i in range(1000)]
        }

    def test_deep_access_performance(self):
        """Test performance of deep access operations."""
        iterations = 1000
        
        # Test accessor performance
        start = time.time()
        for i in range(iterations):
            result = _.level.level.level.level.level.value(self.deep_data)
        accessor_time = time.time() - start
        
        # Test direct access performance
        start = time.time()
        for i in range(iterations):
            result = self.deep_data['level']['level']['level']['level']['level']['value']
        direct_time = time.time() - start
        
        # Document the performance difference
        ratio = accessor_time / direct_time if direct_time > 0 else float('inf')
        
        print(f"\nDeep Access Performance (1000 iterations):")
        print(f"Accessor time: {accessor_time:.4f}s")
        print(f"Direct time: {direct_time:.4f}s")
        print(f"Accessor is {ratio:.1f}x slower than direct access")
        
        # The accessor is significantly slower than direct access - this is a known limitation
        # Document the performance characteristics for users
        self.assertLess(ratio, 200, "Accessor should not be more than 200x slower than direct access")

    def test_list_access_performance(self):
        """Test performance of list access operations."""
        iterations = 100
        
        # Test accessor performance
        start = time.time()
        for i in range(iterations):
            result = _.items.id(self.large_list_data)
        accessor_time = time.time() - start
        
        # Test direct access performance
        start = time.time()
        for i in range(iterations):
            result = [item['id'] for item in self.large_list_data['items']]
        direct_time = time.time() - start
        
        # Document the performance difference
        ratio = accessor_time / direct_time if direct_time > 0 else float('inf')
        
        print(f"\nList Access Performance (100 iterations):")
        print(f"Accessor time: {accessor_time:.4f}s")
        print(f"Direct time: {direct_time:.4f}s")
        print(f"Accessor is {ratio:.1f}x slower than direct access")
        
        # The accessor should be slower but not excessively so
        self.assertLess(ratio, 50, "Accessor should not be more than 50x slower than direct access")

    def test_memory_usage(self):
        """Test memory usage of accessor objects."""
        import sys
        
        # Create accessor objects
        accessor1 = _.a.b.c
        accessor2 = _.a.b.c.d.e.f.g.h.i.j
        
        size1 = sys.getsizeof(accessor1)
        size2 = sys.getsizeof(accessor2)
        
        print(f"\nMemory Usage:")
        print(f"Simple accessor (_.a.b.c): {size1} bytes")
        print(f"Deep accessor (_.a.b.c.d.e.f.g.h.i.j): {size2} bytes")
        
        # Accessor objects should be reasonably sized
        self.assertLess(size1, 1000, "Simple accessor should be less than 1KB")
        self.assertLess(size2, 2000, "Deep accessor should be less than 2KB")

    def test_creation_performance(self):
        """Test performance of accessor creation."""
        iterations = 1000
        
        # Test accessor creation performance
        start = time.time()
        for i in range(iterations):
            accessor = _.a.b.c.d.e
        creation_time = time.time() - start
        
        print(f"\nAccessor Creation Performance (1000 iterations):")
        print(f"Creation time: {creation_time:.4f}s")
        print(f"Average per accessor: {creation_time/iterations*1000:.2f}ms")
        
        # Accessor creation should be reasonably fast
        self.assertLess(creation_time, 1.0, "Accessor creation should be fast")

    def test_large_data_handling(self):
        """Test handling of very large data structures."""
        # Create a very large data structure
        large_data = {
            'items': [{'id': i, 'value': i * 2, 'nested': {'deep': i * 3}} for i in range(10000)]
        }
        
        # Test that accessor can handle large data
        start = time.time()
        result = _.items.id(large_data)
        access_time = time.time() - start
        
        print(f"\nLarge Data Handling:")
        print(f"Accessing 10,000 items: {access_time:.4f}s")
        print(f"Result length: {len(result)}")
        
        # Should handle large data reasonably well
        self.assertEqual(len(result), 10000)
        self.assertLess(access_time, 1.0, "Should handle large data in reasonable time")


if __name__ == '__main__':
    unittest.main()
