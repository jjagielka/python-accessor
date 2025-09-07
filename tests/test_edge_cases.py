"""Comprehensive edge case tests for the accessor library."""

import unittest
from accessor import accessor as _, values, select, items, keys


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_none_input(self):
        """Test handling of None input."""
        self.assertIsNone(_.a.b.c(None))
        self.assertIsNone(_.a[0](None))
        self.assertIsNone(_.a.b.c.d.e.f(None))

    def test_empty_dict(self):
        """Test handling of empty dictionary."""
        self.assertIsNone(_.a.b.c({}))
        self.assertIsNone(_.a[0]({}))

    def test_empty_list(self):
        """Test handling of empty list."""
        self.assertIsNone(_.items[0]([]))
        self.assertIsNone(_.items[0]({}))

    def test_non_dict_input(self):
        """Test handling of non-dictionary input."""
        self.assertIsNone(_.a.b.c("string"))
        self.assertIsNone(_.a.b.c(123))
        self.assertIsNone(_.a.b.c(True))
        # Lists are handled specially - they return a list of None values
        self.assertIsNone(_.a.b.c([1, 2, 3]))

    def test_missing_keys(self):
        """Test handling of missing keys."""
        data = {"a": 1}
        self.assertIsNone(_.b.c(data))
        self.assertIsNone(_.a.b.c(data))
        self.assertIsNone(_.nonexistent.key(data))

    def test_list_index_out_of_range(self):
        """Test handling of list index out of range."""
        data = {"items": [1, 2]}
        self.assertIsNone(_.items[5](data))
        self.assertIsNone(_.items[-10](data))

    def test_deep_nesting(self):
        """Test deep nesting scenarios."""
        # Create deeply nested structure
        data = {}
        current = data
        for i in range(5):  # Reduced depth for testing
            current["level"] = {}
            current = current["level"]
        current["value"] = "deep"

        self.assertEqual(_.level.level.level.level.level.value(data), "deep")

    def test_mixed_data_types(self):
        """Test with mixed data types."""
        data = {
            "string": "hello",
            "number": 42,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
            "none": None,
        }

        self.assertEqual(_.string(data), "hello")
        self.assertEqual(_.number(data), 42)
        self.assertTrue(_.boolean(data))
        self.assertEqual(_.list(data), [1, 2, 3])
        self.assertEqual(_.dict.nested(data), "value")
        self.assertIsNone(_.none(data))

    def test_slice_operations(self):
        """Test slice operations."""
        data = {"items": [1, 2, 3, 4, 5]}

        self.assertEqual(_.items[1:3](data), [2, 3])
        self.assertEqual(_.items[:2](data), [1, 2])
        self.assertEqual(_.items[3:](data), [4, 5])
        self.assertEqual(_.items[::2](data), [1, 3, 5])

    def test_list_of_dicts(self):
        """Test accessing list of dictionaries."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35},
            ]
        }

        self.assertEqual(_.users.name(data), ["Alice", "Bob", "Charlie"])
        self.assertEqual(_.users.age(data), [30, 25, 35])
        self.assertEqual(_.users[0].name(data), "Alice")
        self.assertEqual(_.users[1].age(data), 25)

    def test_comparison_operations(self):
        """Test comparison operations."""
        data = [(1, 2), (3, 2), (5, 4)]
        self.assertEqual(list(filter(_[0] < 3, data)), [(1, 2)])

    def test_values_function(self):
        """Test values function."""
        data = {"a": 1, "b": 2, "c": 3}
        result = values(_.a, _.b, _.c)(data)
        self.assertEqual(result, (1, 2, 3))

    def test_select_function(self):
        """Test select function."""
        data = {"a": 1, "b": 2, "c": 3}
        result = select(_.a, _.b, x=_.c)(data)
        self.assertEqual(result, {"a": 1, "b": 2, "x": 3})

    def test_items_function(self):
        """Test items function."""
        data = {"a": 1, "b": 2}
        result = items(_.a, _.b, prefix="field_")(data)
        self.assertEqual(result, {"field_a": 1, "field_b": 2})

    def test_keys_function(self):
        """Test keys function."""
        data = {"a": 1, "b": 2}
        result = keys(_.a, _.b)(data)
        self.assertEqual(result, ("a", "b"))

    def test_path_tracking(self):
        """Test path tracking functionality."""
        accessor = _.a.b.c.d
        self.assertEqual(accessor._path, "a.b.c.d")
        self.assertEqual(accessor._name, "d")

        accessor2 = _.items[0].name
        self.assertEqual(accessor2._path, "items.0.name")
        self.assertEqual(accessor2._name, "name")

        accessor3 = _.items[1:3].name
        self.assertEqual(accessor3._path, "items[1:3].name")
        self.assertEqual(accessor3._name, "name")

    def test_repr_functionality(self):
        """Test string representation."""
        accessor = _.a.b.c
        self.assertEqual(repr(accessor), "<Accessor 'a.b.c'>")

        accessor2 = _.items[0]
        self.assertEqual(repr(accessor2), "<Accessor 'items.0'>")

    def test_special_characters_in_keys(self):
        """Test handling of special characters in keys."""
        data = {
            "key-with-dash": 1,
            "key_with_underscore": 2,
            "key.with.dots": 3,
            "key with spaces": 4,
        }

        # Test underscore works (valid Python identifier)
        self.assertEqual(_.key_with_underscore(data), 2)

        # Test that other special characters don't work with dot notation
        self.assertIsNone(_.key_with_dash(data))  # This won't work due to hyphen
        # The others would need bracket notation which isn't implemented

    def test_very_large_structures(self):
        """Test with very large data structures."""
        # Create a large list
        large_list = [{"id": i, "value": i * 2} for i in range(1000)]
        data = {"items": large_list}

        # Test accessing the list
        result = _.items(data)
        self.assertEqual(len(result), 1000)

        # Test accessing specific items
        self.assertEqual(_.items[0].id(data), 0)
        self.assertEqual(_.items[999].id(data), 999)

        # Test accessing all IDs
        ids = _.items.id(data)
        self.assertEqual(len(ids), 1000)
        self.assertEqual(ids[0], 0)
        self.assertEqual(ids[999], 999)


if __name__ == "__main__":
    unittest.main()
