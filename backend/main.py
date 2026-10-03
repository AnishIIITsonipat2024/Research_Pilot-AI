from backend.graph.workflow import create_workflow


def main():

    app = create_workflow()

    query = input(
        "\n🔬 Enter research topic: "
    )

    result = app.invoke({
        "query": query
    })

    print("\n\n========== FINAL REPORT ==========\n")

    print(
        result.get(
            "final_report",
            "No report generated."
        )
    )


if __name__ == "__main__":
    main()