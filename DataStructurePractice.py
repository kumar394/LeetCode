# define a function to find the missing number in an array of integers from 0 to n
def missing_num(nums):
    n = len(nums)
    expected_sum= n*(n+1)//2
    actual_sum= sum(nums)
    missing_num= expected_sum - actual_sum
    return missing_num


def missing_number(nums):
    """
    Finds the missing number in an array of integers from 0 to n.

    Args:
        nums: A list of integers from 0 to n, with one number missing.

    Returns:
        The missing number.
    """
    n = len(nums)
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    return expected_sum - actual_sum


def bin_min_max(str):

    """
    Finds the first, last, min, max for a comma separated string data having log for each timestamp and trade count.

    Args:
        str: log of timestamp and trades in string format

    Returns:
        A dictionary with first, last, min and max for each bin of 10.
    """

    data_list= str.split(",")
    data= [(float(data_list[i]), float(data_list[i+1])) for i in range(0, len(data_list), 2)]
            
    bin= {}

    for i in data:
        bin_key= i[0]//10

        if bin_key not in bin:
            bin[bin_key]= {"min": i[1],
                           "max": i[1],
                           "first": i[1],
                           "last": i[1]
                           }
        else:
            bin[bin_key]= {"min": min(i[1], bin[bin_key]["min"]),
                           "max": max(i[1], bin[bin_key]["max"]),
                           "first": bin[bin_key]["first"],
                           "last": i[1]
                           }

    return bin

s= "100,1,105,5,102,12,110,15,120,22,115,29"
print(bin_min_max(s))

a= "I am a good boy and have lot of toys"
print (a.lower)


def bigram(s):
    """
    This function returns bigrams
    """
    a = s.split(" ")
    bg= [(a[i], a[i+1]) for i in range(len(a)-1)]
    return bg


sentence = "Have free hours and love children"
print (bigram(sentence))

def repeatchar (s):
    a = []
    for i in s:
        if i in a:
            return i
        else:
            a.append(i)  

s = "interviewquery"

print(repeatchar(s))

def validparenthesis(s):

    """
    This function returns if the string is valid parenthesis
    """
    
    map_paren= {"(":")", "{":"}", "[":"]"}
    
    stk= []
    for i in s:
        if i in map_paren.keys():
            stk.append(i)
            
        elif i in map_paren.values() and stk:
            last= stk.pop()
            if i != map_paren[last]:
                return False
            
        else:
            return False
        
    if stk:
        return False
    
    else:
        return True