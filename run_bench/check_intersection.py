def check_intersect(heat_set):
    while True:
        merged = set()
        for tuple1 in heat_set:
            remaining_counter = len(heat_set) - 1
            for tuple2 in heat_set:
                if tuple1 != tuple2:
                    if tuple1[1] >= tuple2[0] and tuple1[0] <= tuple2[1]:
                        merged.add((min(tuple1[0], tuple2[0]), max(tuple1[1], tuple2[1])))
                    else:
                        remaining_counter -= 1
            if remaining_counter == 0:
                merged.add(tuple1)
        if merged == heat_set:
            break
        else:
            heat_set = merged.copy()
    return heat_set

heat_set = set()

heat_set.add((140736902758536,140737346482200))
heat_set.add((140733949701048,140735204367960))
heat_set.add((140733452424528,140733919099416))
heat_set.add((140736397831608,140736849205680))
heat_set.add((140735303823264,140735808750192))
heat_set.add((140722948414344,140723208528216))

res = check_intersect(heat_set)
print(res)