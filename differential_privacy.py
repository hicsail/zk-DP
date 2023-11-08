from picozk import *

if __name__ == "__main__":
    scale = 10

    p = pow(2, 61) - 1

    with PicoZKCompiler("picozk_test", field=[p], options=["ram"]):
        print(scale)
