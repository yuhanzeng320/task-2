import base64
import json
import requests
import math

def main():
    base_url = input("Please enter the URL:  ")

    # Step 1: Get the RSA modulus N from the server
    web_return = requests.get(f'{base_url}/pk/')
    N = web_return.json()['N']

    desired_output = "You got a 12 because you are an excellent student! :)"
    desired_output_bytes = desired_output.encode()
    desired_output_int = int.from_bytes(desired_output_bytes, "big")

    # Step 2: Divide the required output into two parts
    part1_int = desired_output_int // 5
    part2_int = 5
    n_bytes = math.ceil(int.bit_length(N) / 8)
    part1_bytes = part1_int.to_bytes(n_bytes, 'big')
    part2_bytes = part2_int.to_bytes(n_bytes, 'big')

    # Step 3: Get signatures for both parts
    ## Obtain a signed message for part1
    web_return = requests.get(f'{base_url}/sign_random_document_for_students/{part1_bytes.hex()}')
    signature_part1 = web_return.json().get('signature')

    ## Obtain a signed message for part2
    web_return = requests.get(f'{base_url}/sign_random_document_for_students/{part2_bytes.hex()}')
    signature_part2 = web_return.json().get('signature')

    # Step 4: Multiply the signatures to obtain the desired signature
    s1 = int.from_bytes(bytes.fromhex(signature_part1), 'big')
    s2 = int.from_bytes(bytes.fromhex(signature_part2), 'big')
    fake_signature_int = (s1 * s2) % N
    fake_signature = fake_signature_int.to_bytes(math.ceil(int.bit_length(N) / 8), 'big')

    # Step 5: Craft a JSON object with the fake signature
    fake_json = json.dumps({'msg': desired_output_bytes.hex(), 'signature': fake_signature.hex()})

    # Step 6: Encode JSON data into a cookie-friendly format
    fake_cookie = base64.b64encode(fake_json.encode(), altchars=b'-_').decode()

    # Step 7: Send the fake cookie to the server using /grade instead of /quote
    web_return = requests.get(f'{base_url}/grade/', cookies={'grade': fake_cookie})
    print(web_return.text)

if __name__ == "__main__":
    main()
