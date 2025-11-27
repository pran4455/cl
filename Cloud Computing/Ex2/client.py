import Pyro4

def main():
    uri = input("Enter the server URI: ")
    calculator = Pyro4.Proxy(uri)  # Create proxy for remote object

    try:
        a = int(input("Enter first number: "))
        b = int(input("Enter second number: "))

        result_add = calculator.add_numbers(a, b)
        result_mul = calculator.multiply(a, b)

        print(f"Addition result: {result_add}")
        print(f"Multiplication result: {result_mul}")

    except ValueError:
        print("Invalid input. Please enter integers.")
    except Exception as e:
        print("Error during remote call:", e)

if __name__ == "__main__":
    main()
