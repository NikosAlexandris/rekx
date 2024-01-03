# Concepts

## Parallel

_Parallel_
are operations running _simultaneously_ yet _independently_
in multiple threads, processes or machines.
For CPU-intensive workloads,
past the overhead of arranging such a system,
a speedup equal to the number of CPU cores is possible.

| Parallel access with | Scenario                                                                         |
|----------------------|----------------------------------------------------------------------------------|
| Lock                 | Resource A (locked) -> Process 1                                                 |
| No Lock              | Resource A $\longrightarrow$ Process 1<br>Resource A $\longrightarrow$ Process 2 |


## Concurrent

_Concurrent_
are multiple operations managed during overlapping periods
yet not necessarily executed at the exact same instant.
For the particular case of cloud storage,
the latency to get the first byte of a read can be comparable
or dominate the total time for a request.
Practically, launching many requests,
and only pay the overhead cost once (they all wait together),
enables a large speedup.


|      Execution | Task                                                                                                                                                                                                                                                             |
|---------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Non-Concurrent | A $\rightarrow$ Run $\rightarrow$ Complete $\longrightarrow$ B $\rightarrow$ Run $\rightarrow$ Complete                                                                                                                                                          |
|     Concurrent | A $\rightarrow$ .. $\rightarrow$ Complete<br> .. B $\longrightarrow$ .. $\rightarrow$ Complete<br>C $\longrightarrow$ .. $\longrightarrow$ Complete<br> .. .. D $\longrightarrow$ .. $\rightarrow$ Complete<br> .. E $\rightarrow$ .. $\longrightarrow$ Complete |


## Chunks

Reading a chunk?

| Byte range |               Index              |
|-----------:|:--------------------------------:|
|   Original | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` |
|  Selection |          `[3, 4, 5, 6]`          |


## Descriptive metadata

|  Compression | Size                             |  % |
|-------------:|:---------------------------------|---:|
| Decompressed | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` |  0 |
|   Compressed | `[0, 1, 2, 3, 4, 5, 6]`          | 30 |


## Consolidation

A single indexible aggregate dataset

| Consolidation |        Data       | Parts |
|--------------:|:-----------------:|:-----:|
|     Scattered | `[-]` `[-]` `[-]` |   3   |
|  Consolidated |  `[-----------]`  |   1   |


|             Aggregation | Simple | Simple | Virtual |
|------------------------:|:------:|:------:|:-------:|
|                    File |    A   |    B   |    V    |
| Points to $\rightarrow$ |    A   |    B   |   A, B  |


## Asynchronous

_Asynchronous_
is a mechanism performing tasks without waiting for other tasks to complete.

|    Operation | Execution                                                                                                                                                      |
|-------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
|   Sequential | A $\longrightarrow$ Complete $\rightarrow$ B $\longrightarrow$ Complete $\rightarrow$ C $\longrightarrow$ Complete                                             |
| Asynchronous | A $\longrightarrow$ .. $\longrightarrow$ Complete<br>B $\longrightarrow$ .. .. $\longrightarrow$ Complete<br>C $\longrightarrow$ .. $\longrightarrow$ Complete |


## Serverless

_Serverless_
is a deployment of code in a cloud service which in turn handles
server maintenance, scaling, updates and more. 

| Deployment  | Management                                       |
|-------------|--------------------------------------------------|
| Traditional | Manual server, maintenance, scaling, updates, .. |
| Serverless  | Automated cloud service, deployment, scaling, .. |


## Front- and Back-end

| Component | Role                                                        |
|-----------|-------------------------------------------------------------|
| Backend   | Data storage, algorithms, API, processing, serving          |
| Frontend  | User interface & experience using a browsers or application |
