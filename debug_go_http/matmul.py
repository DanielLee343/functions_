from numpy import matrix, linalg, random

n=10
# Create AxA array of random numbers -0.5 to 0.5
A = random.random_sample((n, n)) - 0.5
# print(type(A))
B = A.sum(axis=1)
# print(B)

# Convert to matrices
A = matrix(A)
print((A))
B = matrix(B.reshape((n, 1)))
print(B)
x = linalg.solve(A, B)
print(x)