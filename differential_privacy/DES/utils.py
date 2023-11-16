import random

def list_to_binary(_list):
    return int(''.join(map(str, _list)), 2)

def int_to_bitlist(num, size=None):
    if size is None:
      return [int(x) for x in bin(num)[2:]]
    else:
      return [int(x) for x in format(num, f'0{size}b')]


# Generate 'size' bits
def generate_bit(size):
    bit = random.randint(0, 2**size)
    bit_list = int_to_bitlist(bit, size)
    return bit, bit_list


def sign(one, two):

  if len(one)>len(two):
    two = [0 for _ in range(len(one) - len(two))] + two
  elif len(one)<len(two):
    one = [0 for _ in range(len(two) - len(one))] + one

  assert len(one) == len(two) #TODO: Make this more flexy
  signed_x_list = [0 for _ in range(len(one))]
  for i, (x, k) in enumerate(zip(one, two)):
      if int(x) - int(k) !=0:
        signed_x_list[i] = 1
      else:
        signed_x_list[i] = 0
  return signed_x_list

assert sign([0, 1, 1, 0], [1, 0, 1, 0]) == [1, 1, 0, 0]
assert sign([0, 1, 0, 1, 1, 0], [1, 0, 1, 0]) == [0, 1, 1, 1, 0, 0]