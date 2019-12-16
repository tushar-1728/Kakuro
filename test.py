def findCombinationsUtil(arr, index, num, reducedNum, size, comb):
	if (reducedNum < 0):
		return
	if (reducedNum == 0 and index == size):
		temp = []
		for i in range(index):
			temp.append(arr[i])
		comb.append(temp)
		return
	prev = 1 if(index == 0) else arr[index - 1] + 1;
	for k in range(prev, 10):
		arr[index] = k;
		findCombinationsUtil(arr, index + 1, num, reducedNum - k, size, comb)

def findCombinations(n, size):
	arr = [0] * n
	comb = []
	findCombinationsUtil(arr, 0, n, n, size, comb)
	print(comb)

n = 22
size = 4
findCombinations(n, size);


def sort(lst):
	lst.sort(key = lambda x: x[2]) 
	return lst 

sub_li =[['rishav', 10], ['akash', 5], ['ram', 20], ['gaurav', 15]] 
print(sort(sub_li)) 