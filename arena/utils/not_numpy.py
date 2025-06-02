"""
not-numpy: Numpy replacement for util quaternion/matrix operations
Supports all slice operations: mat[0:3, 0:3], mat[0:3, 3], etc.
"""

import math


class NDArray:
    """Complete array class that mimics numpy.ndarray for specifically euler/quat utils."""

    def __init__(self, data):
        if isinstance(data, (list, tuple)):
            # Handle nested lists (2D arrays)
            if data and isinstance(data[0], (list, tuple)):
                self.data = [list(row) for row in data]  # Deep copy
                self.shape = (len(data), len(data[0]))
                self.ndim = 2
            else:
                self.data = list(data)
                self.shape = (len(data),)
                self.ndim = 1
        else:
            self.data = [data]
            self.shape = (1,)
            self.ndim = 0

    def __iter__(self):
        """Make NDArray iterable like numpy arrays."""
        if self.ndim == 2:
            # Return each row as an NDArray
            for row in self.data:
                yield NDArray(row)
        else:
            # 1D array - iterate over elements
            for item in self.data:
                yield item

    def tolist(self):
        """Convert to nested Python lists like numpy."""
        return self.data

    def _parse_slice_index(self, key, max_val):
        """Convert slice or int to range indices."""
        if isinstance(key, slice):
            start, stop, step = key.indices(max_val)
            if step != 1:
                raise NotImplementedError("Slice step != 1 not supported")
            return list(range(start, stop))
        elif isinstance(key, int):
            if key < 0:
                key += max_val
            return [key]
        else:
            raise TypeError(f"Invalid index type: {type(key)}")

    def __getitem__(self, key):
        """Support numpy-style indexing including slices."""
        if isinstance(key, tuple) and len(key) == 2:
            # 2D indexing: arr[row_spec, col_spec]
            row_spec, col_spec = key

            row_indices = self._parse_slice_index(row_spec, self.shape[0])
            col_indices = self._parse_slice_index(col_spec, self.shape[1])

            # Extract the subarray
            if len(row_indices) == 1 and len(col_indices) == 1:
                # Single element
                return self.data[row_indices[0]][col_indices[0]]
            elif len(row_indices) == 1:
                # Single row, multiple columns
                result = [self.data[row_indices[0]][c] for c in col_indices]
                return NDArray(result)
            elif len(col_indices) == 1:
                # Multiple rows, single column
                result = [self.data[r][col_indices[0]] for r in row_indices]
                return NDArray(result)
            else:
                # Multiple rows and columns
                result = []
                for r in row_indices:
                    row_data = [self.data[r][c] for c in col_indices]
                    result.append(row_data)
                return NDArray(result)

        elif isinstance(key, slice) and self.ndim == 2:
            # Row slice: arr[0:3] on 2D array
            row_indices = self._parse_slice_index(key, self.shape[0])
            result = [self.data[r] for r in row_indices]
            return NDArray(result)

        elif isinstance(key, slice) and self.ndim == 1:
            # Slice on 1D array
            indices = self._parse_slice_index(key, self.shape[0])
            result = [self.data[i] for i in indices]
            return NDArray(result)

        elif self.ndim == 2:
            # Single index on 2D array returns row as NDArray
            return NDArray(self.data[key])
        else:
            # 1D array indexing
            return self.data[key]

    def __setitem__(self, key, value):
        """Support numpy-style assignment including slices."""
        if isinstance(key, tuple) and len(key) == 2:
            # 2D assignment: arr[row_spec, col_spec] = value
            row_spec, col_spec = key

            row_indices = self._parse_slice_index(row_spec, self.shape[0])
            col_indices = self._parse_slice_index(col_spec, self.shape[1])

            # Convert value to usable format
            if isinstance(value, NDArray):
                val_data = value.data
            elif isinstance(value, (list, tuple)):
                val_data = value
            else:
                val_data = [[value] * len(col_indices)] * len(row_indices)

            # Handle different assignment patterns
            if len(row_indices) == 1 and len(col_indices) == 1:
                # Single element assignment
                self.data[row_indices[0]][col_indices[0]] = value
            elif len(row_indices) == 1:
                # Single row, multiple columns: arr[0, 0:3] = [1,2,3]
                for i, c in enumerate(col_indices):
                    self.data[row_indices[0]][c] = val_data[i] if isinstance(val_data, (list, tuple)) else val_data
            elif len(col_indices) == 1:
                # Multiple rows, single column: arr[0:3, 0] = [1,2,3]
                for i, r in enumerate(row_indices):
                    self.data[r][col_indices[0]] = val_data[i] if isinstance(val_data, (list, tuple)) else val_data
            else:
                # Multiple rows and columns: arr[0:3, 0:3] = matrix
                if isinstance(val_data[0], (list, tuple)):
                    # 2D value
                    for i, r in enumerate(row_indices):
                        for j, c in enumerate(col_indices):
                            self.data[r][c] = val_data[i][j]
                else:
                    # 1D value - broadcast
                    for i, r in enumerate(row_indices):
                        for j, c in enumerate(col_indices):
                            self.data[r][c] = val_data[i * len(col_indices) + j]

        elif isinstance(key, slice) and self.ndim == 2:
            # Row slice assignment: arr[0:3] = [[1,2,3], [4,5,6], [7,8,9]]
            row_indices = self._parse_slice_index(key, self.shape[0])
            if isinstance(value, NDArray):
                val_data = value.data
            else:
                val_data = value

            for i, r in enumerate(row_indices):
                if isinstance(val_data[i], (list, tuple)):
                    self.data[r] = list(val_data[i])
                else:
                    self.data[r] = [val_data[i]] * self.shape[1]

        elif isinstance(key, slice) and self.ndim == 1:
            # 1D slice assignment
            indices = self._parse_slice_index(key, self.shape[0])
            if isinstance(value, (list, tuple, NDArray)):
                val_list = value.data if isinstance(value, NDArray) else value
                for i, idx in enumerate(indices):
                    self.data[idx] = val_list[i]
            else:
                for idx in indices:
                    self.data[idx] = value
        else:
            # Simple assignment
            if self.ndim == 2:
                # Setting entire row
                if isinstance(value, NDArray):
                    self.data[key] = value.data
                elif isinstance(value, (list, tuple)):
                    self.data[key] = list(value)
                else:
                    self.data[key] = [value] * self.shape[1]
            else:
                self.data[key] = value

    def __matmul__(self, other):
        """Matrix multiplication using @ operator."""
        if self.ndim == 2 and other.ndim == 2:
            rows_a, cols_a = self.shape
            rows_b, cols_b = other.shape

            if cols_a != rows_b:
                raise ValueError("Matrix dimensions don't match for multiplication")

            result = []
            for i in range(rows_a):
                row = []
                for j in range(cols_b):
                    val = 0.0
                    for k in range(cols_a):
                        val += self.data[i][k] * other.data[k][j]
                    row.append(val)
                result.append(row)

            return NDArray(result)
        else:
            raise NotImplementedError("Only 2D @ 2D multiplication supported")

    def __pow__(self, power):
        """Element-wise power: arr ** 2"""
        if self.ndim == 2:
            result = []
            for row in self.data:
                new_row = [x ** power for x in row]
                result.append(new_row)
            return NDArray(result)
        else:
            result = [x ** power for x in self.data]
            return NDArray(result)

    def __repr__(self):
        if self.ndim == 2:
            return f"NDArray({self.data})"
        else:
            return f"NDArray({self.data})"


def array(data):
    """Create NDArray from list/nested list."""
    return NDArray(data)


def identity(n):
    """Create n×n identity matrix."""
    result = []
    for i in range(n):
        row = [0.0] * n
        row[i] = 1.0
        result.append(row)
    return NDArray(result)


def diag(values):
    """Create diagonal matrix from values."""
    if isinstance(values, NDArray):
        vals = values.data
    else:
        vals = values

    n = len(vals)
    result = []
    for i in range(n):
        row = [0.0] * n
        row[i] = vals[i]
        result.append(row)
    return NDArray(result)


def sqrt(x):
    """Element-wise or scalar square root."""
    if isinstance(x, NDArray):
        if x.ndim == 2:
            result = []
            for row in x.data:
                new_row = [math.sqrt(val) for val in row]
                result.append(new_row)
            return NDArray(result)
        else:
            result = [math.sqrt(val) for val in x.data]
            return NDArray(result)
    else:
        return math.sqrt(x)


def copysign(x, y):
    """Apply sign of y to magnitude of x."""
    return math.copysign(x, y)


# Store reference to builtin sum before we override it
builtin_sum = sum


def sum(arr, axis=None):
    """Sum array elements along specified axis."""
    if isinstance(arr, NDArray):
        if arr.ndim == 2 and axis == 0:
            # Sum along rows (down columns)
            cols = arr.shape[1]
            result = []
            for j in range(cols):
                col_sum = 0.0
                for i in range(arr.shape[0]):
                    col_sum += arr.data[i][j]
                result.append(col_sum)
            return NDArray(result)
        elif arr.ndim == 2 and axis == 1:
            # Sum along columns (across rows)
            result = []
            for row in arr.data:
                result.append(builtin_sum(row))
            return NDArray(result)
        else:
            # Sum all elements
            total = 0.0
            if arr.ndim == 2:
                for row in arr.data:
                    total += builtin_sum(row)
            else:
                total = builtin_sum(arr.data)
            return total
    else:
        return builtin_sum(arr)


def max(x, default_val):
    """Return max of x and default_val."""
    if x > default_val:
        return x
    else:
        return default_val