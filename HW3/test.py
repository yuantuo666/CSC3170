import math

print(1 + math.ceil(math.log(200000, 59)))


print(sum([math.ceil(12000000 / (2 ** i * 60)) for i in range(3)]))

n_b = 12000000 / 60

print(n_b + n_b/2 + n_b/4)

print(1 + math.ceil(math.log(12000000 / 120, 119)))

print(math.log(200000, 59), math.log(100000, 119))

B = 3

print(1 + math.ceil(math.log(12000000 / B, B - 1)))

N = 345600
B = 25

print(1 + math.ceil(math.log(N / B, B - 1)))

N = 800
B = 500

print(1 + math.ceil(math.log(N / B, B - 1)))