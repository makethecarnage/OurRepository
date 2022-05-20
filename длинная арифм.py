ms = [1]
curr_num = 0
previous = [0]
summ = 0

for i in range(2, 16):
    for j in range(len(nums) - 1, -1, -1):
        if nums[j] > 9:
            num = nums[j]
            nums[j] = num % 10
            nums[j - 1] += num // 10

        num = nums[j] * i

        nums[j] = num % 10

        if num > 9 and num < 100:


            if j == 0:
                nums.insert(0, 0)
                nums[j] += num // 10
                previous.insert(0, 0)
                if previous[j+1] != 0:
                    nums[j+1] += previous[j+1]
                    previous[j+1] = 0
                    for q in range(j+1, 0, -1):
                        if nums[q] > 9:
                            num = nums[q]
                            nums[q] = num % 10
                            nums[q- 1] += num // 10

            else:
                previous[j-1] = num // 10


        elif num > 99:
            if j == 0:
                nums.insert(0, 0)
                nums.insert(0, 0)
                nums[j+1] += num // 10 % 10
                nums[j] = num // 100
                previous.insert(0, 0)
                previous.insert(0, 0)
                if previous[j+1] != 0:
                    nums[j+1] += previous[j+1]
                    previous[j+1] = 0
                if previous[j+2] != 0:
                    nums[j+2] += previous[j+2]
                    previous[j+2] = 0
                for q in range(j + 1, 0, -1):
                    if nums[q] > 9:
                        num = nums[q]
                        nums[q] = num % 10
                        nums[q - 1] += num // 10

            elif j == 1:
                previous[j - 1] += num // 10 % 10
                nums.insert(0, 0)
                nums[j-1] += num // 100

            else:
                previous[j - 1] += num // 10 % 10
                previous[j - 2] += num // 100

        if previous[j] != 0:
            nums[j] += previous[j]
            previous[j] = 0
            for q in range(j+1, 0, -1):
                if nums[q] > 9:
                    num = nums[q]
                    nums[q] = num % 10
                    nums[q - 1] += num // 10

    print(nums)


print(len(nums))
