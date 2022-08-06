import unittest
import os
import sys

sys.path.append(os.getcwd() + '/../')

from gizligizli import *


class Test(unittest.TestCase):
    # >>> os.urandom(243).hex()
    sc_placeholder = '2315e6a08e999543fe2b022ccaa94420986203a53382e1e6e55aa99b7d078c1d9e42f94e55b5c2a9f05e29db8d8f499ebf79bee56d728e21aad1c6025a9518e5a57a9b1dfd81453821136b14b4106e0d1c8d8f92be0d668161c582bef3d296417830781049429a8f08e304add9464a7a8847d61939412142a2fa2321b3163503b462c6b4a8718c141f4e469b5b9ffb1a47402c5a805f59b21e60e84d24f3cc1a70339b60a2288c335b7a7f2e5b074f8d648bdab19937f1a22c798aa275c0db3e06fa35922cd51bd93ee76902b4841138380304aeed276e6327d7dbb231b7bf56b9209928071d97c0f9f79e5cdff8612607488c'
    sc_file = "shellcode.bin"
    source_icon = "test.ico"
    target_icon = "embedded_test.ico"

    f = open(sc_file, "wb")
    print(bytes.fromhex(sc_placeholder).hex())
    f.write(bytes.fromhex(sc_placeholder))
    f.close()
    
    def test_hide_and_unhide(self):
        # hide
        hide(self.sc_file, self.source_icon, self.target_icon)
    
        # unhide
        extracted_sc = unhide(self.target_icon) # embedded_test.ico
        print(f"Extracted shellcode: {extracted_sc}")

        first_condition = len(extracted_sc) == len(self.sc_placeholder)
        second_condition = extracted_sc == self.sc_placeholder
        print(f"First condition: {first_condition}")
        print(f"Second condition: {second_condition}")


        self.assertTrue(first_condition and second_condition)



if __name__ == "__main__":
    
    unittest.main(verbosity=2)
    
