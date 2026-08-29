# Step 1: define your alphabet — a string of all 62 characters
ALPHABET ="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
# (fill in: 0-9, then a-z, then A-Z, all in one string, no separators)

BASE = len(ALPHABET)  # this should naturally come out to 62 — don't hardcode 62 anywhere else


def encode(num: int) -> str:
    # Step 2: handle the special case — what should happen if num is 0?
    if num == 0:
        return ALPHABET[0]  # what's the simplest valid output here?

    # Step 3: prepare an empty list to collect characters
    result = []

    # Step 4: loop while num is still greater than 0
    while num > 0:
        remainder = num % BASE # how do you get the "next digit" in base 62?
        result.append(ALPHABET[remainder])  # turn that remainder into a character using ALPHABET
        num = num // BASE # how do you remove that digit from num before the next loop?

    # Step 5: result is currently backwards — fix that
    result.reverse() # which list method reverses it in place?

    # Step 6: turn the list of characters into one final string
    return "".join(result)


def decode(code: str) -> int:
    num = 0
    for char in code:
        index = ALPHABET.index(char)
        num = num * BASE + index
    return num

if __name__ == "__main__":
    print(encode(125))
    print(decode(encode(125)))
    print(decode(encode(999999)))