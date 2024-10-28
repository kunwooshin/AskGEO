import askgeo.rag.rag_flow as rag


def main():
    # loader.load_data() # need only once

    # welcome message
    print("Welcome to Askgeo!")
    print("Askgeo is a geospatial question answering chat bot.")
    print("You can ask questions about geospatial data in the database.")
    print("Please enter your question in natural language.")
    print("If you want to exit, type 'exit'.")
    print("Let's get started!\n")

    rag.setup()

    while True:
        # user_query = input("Enter your question for the Askgeo: ")
        user_prompt = 'Leonard Gordon Park 자전거 정류장 좌표알려줘'  # 정확한 명칭 입력했다고 가정
        response = rag.prompt(user_prompt)
        print(response)
        exit(-1)

    # TODO implement multi turn


# Entry point
if __name__ == "__main__":
    main()
