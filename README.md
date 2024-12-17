# CSC3170

![Visitors](https://komarev.com/ghpvc/?username=CSC3170&label=VIEWS)

# Repository Information

Learning resources about CSC3170: Database Systems, 2024 Fall @ CUHK-Shenzhen.

## Resources

- [100/100] [HW1](./hw1/HW1.md): SQL writing.
- [95/100] [HW2](./hw2/CSC3170_Assignment2.pdf): -5 for hash table insert order. Tuples calculation + I/O calculation + Hash table + Page replacement algorithm.
- [?/100] [HW3](./hw3/CSC3170_Assignment3.pdf): Merge Algorithm + Join Algorithm + B+Tree implementation.
- [100/100] [Final Project](./Project/Project-CSC3170.pdf): Database management system design + implementation + demo + report.
- [71/100] [Final Exam](./Final/final-review.pdf): See comments below. Distribution: min=14, max=92, median=59.

# Course Information

- **Course Code**: CSC3170
- **Course Name**: Database Systems
- **Term**: 2024-25 Term 2 (Fall)
- **Lecturer**: [Prof. Chenhao Ma](https://chenhao-ma.github.io/)
- **Description**: This is an introductory course in database systems. Topics discussed include database schemas and architectures, relational database, SQL, E-R-model, database design and normalization, indexing and hashing, transaction management, analytic processing, data warehouse and data mining.

## Assessment

- Three assignments (30%)
    - 1st @ week #2, 2nd @ week #5, 3rd @ week #10
- One project (20%)
    - It takes around 1 month to finish, due on week #10
    - Personal project, no group project.
- Final exam (50%)
    - Closed test, no dictionary.
    - One A4 paper for notes (both sides, must handwritten).
    - 2 hours.
- No midterm, no quiz, no signup.

## Target

Different from the previous course, there is more focus on what is inside the **DBMS**.

## Contents

1. Introduction & Relational Model
2. SQL
3. Storage
4. Storage Models
5. Buffer Management
6. Hash Table
7. B+Tree
8. Sorting & aggregation
9. Joins
10. Query execution
11. Query optimization
12. DB Design
13. Transactions & Concurrency control
14. Recovery & Distributed

## Final Exam Comments

1. **Not tested**: 
   1. Definition of the concept.
   2. SQL writing.
   3. Background knowledge, e.g., why we use B+Tree, why we use hash table, etc.
   4. File storage details, e.g., storage page structure, page/tuple layout, etc.
   5. Storage models' definitions/advantages/disadvantages.
   6. Compression.
   7. Processing models.
2. **Do** tests on:
   1. Relational Algebra & SQL (~20%): need to understand different algebra operations and SQL syntax.
   2. B+Tree: major part, insert/delete/search with lock.
   3. Cost Estimation: often asked in the exam.
   4. Latches & Locks: basic and better ones introduced in the course.
   5. Join types: only tests Natural Join.
   6. Dynamic hash table.
   7. Buffer management: clock replacement policy (4%).
3. General reviews:
   1. Many concepts are introduced in the course but not tested, with more focus on the computation part. Understanding also matters.
   2. The cheat sheet actually did not help much, since many topics require understanding.
   3. Not as deep as CMU's course, so make sure you attend/read all lectures and slides.
   4. It's kind of misleading for the review lecture by the TA team, since they only cover around 30% of the course, and half of the introduced content is not tested.

# References

- [CMU 15-445/645](https://15445.courses.cs.cmu.edu/fall2024/)
- [Relational Model & Algebra](https://rulerchen.github.io/RulerChen-Website/docs/CMU15-445/c01/)
