import heapq

stdin = input().strip().split(" ")
n = int(stdin[0])
m = int(stdin[1])

seq = input().strip().split(" ")
seq = [int(i) for i in seq]

# 预处理每个页面的下次使用时间
next_use = [0] * n
next_use_dict = {}
for idx in range(n - 1, -1, -1):
    page = seq[idx]
    if page in next_use_dict:
        next_use[idx] = next_use_dict[page]
    else:
        next_use[idx] = float('inf')
    next_use_dict[page] = idx

cache = set()
heap = []
reads = 0

for idx in range(n):
    page = seq[idx]
    if page in cache:
        # 页面在缓存中，更新其下次使用时间
        heapq.heappush(heap, (-next_use[idx], page))
    else:
        reads += 1  # 需要从磁盘读取页面
        if len(cache) < m:
            cache.add(page)
        else:
            # 缓存已满，需要替换页面
            while heap:
                farthest_next_use, farthest_page = heapq.heappop(heap)
                if farthest_page in cache:
                    cache.remove(farthest_page)
                    break
        cache.add(page)
        heapq.heappush(heap, (-next_use[idx], page))

print(reads)
