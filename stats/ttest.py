import math
from scipy import stats

wins = [1,2,3,4,5,6,7,8,9,10]
mean = [19182.05,19969.51,20498.98,21697.53,21395.16,23708.43,24154.02,21645.03,21377.89,29839.5]
sd = [8272.125,8046.116,8262.663,9088.786,8384.552,8867.445,8132.355,8867.445,8526.908,11287.02]
n = [988,670,493,212,210,96,42,32,18,137]


#s = ((988-1)*8272.125^2 + (137-1)*11287.02^2) / (988+137-2)
csv = ""
for i in range(0,10):
	csv = csv+"\n"
	csv = csv+str(i+1)
	for j in range(0,10):
		print(str(i)+","+str(j))
		if i != j:
			n1 = n[i]
			n2 = n[j]
			x1 = mean[i]
			x2 = mean[j]
			s1 = sd[i]
			s2 = sd[j]

			s = math.sqrt(((n1 - 1)*s1**2 + (n2 - 1)*s2**2)/(n1+n2-2))
			t = (x1 - x2)/(s*math.sqrt(1/n1 + 1/n2))
			print("t is: "+str(t))
			cv = abs(float(stats.t.isf(.975, n1+n2-2)));
			if abs(float(t)) > cv:
				#Reject
				csv = csv+",R"
			else:
				csv = csv+",A"
			print("Critical value: "+str(cv))

		else:
			csv = csv+",O"

print(csv)
