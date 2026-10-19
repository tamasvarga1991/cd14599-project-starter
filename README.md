# Udatracker Order Management System

This project implements an order management backend using Test-Driven Development (TDD). The application provides functionality to create orders, retrieve order details, update order status, list all orders, and filter orders by status through a REST API built with Flask.

## Reflection

- I kept the business logic inside the `OrderTracker` class and used Flask routes only as a thin API layer. This separation made the system easier to test, maintain, and extend.

- Writing unit tests before implementing functionality helped define the expected behavior early. Multiple failing tests immediately revealed missing validation and edge cases, which guided the implementation.

- Following the Red → Green → Refactor cycle made development more structured. Each feature was implemented incrementally only after a failing test had been created and verified.

- If I continued this project, I would replace the in-memory storage with a persistent database such as SQLite so that orders remain available after restarting the application.

- Additional future improvements could include DELETE endpoints, stronger input validation, and more advanced filtering options.