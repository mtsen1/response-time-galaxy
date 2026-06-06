# Response-Time Galaxy: Device Profile and Response Time Latency

An interactive 3D data visualization dashboard that maps cognitive assessment response time performance across different hardware profiles and browser engines. By transforming traditional behavioral metrics into a multi-layered topology, this project reveals how system memory, graphics architectures, and browser environments systematically shape user latency and response stability.

[View the Interactive Plot](https://mtsen1.github.io/response-time-galaxy/)


## Project Architecture & Visual Language

The overall coordinates are mapped across three multi-dimensional axes:
* **X-Axis:** Performance (Mean FPS)
* **Y-Axis:** Instability (Coefficient of Variation of FPS)
* **Z-Axis:** Speed of Response (Response Time in ms)

### Star Sizing (Behavioral Variance)
Individual user trial dots are scaled to represent intra-individual behavioral variance, measuring how much a single participant's reaction time fluctuates or drifts during a task, rather than just their raw speed.

The data pipeline groups the dataset by participant (`pid`), calculates the standard deviation ($SD$) of their reaction times, and bins them into four equal population quantiles:

| Quantile Position | Behavioral Meaning | Visual Star Class | Map Size |
| :--- | :--- | :--- | :--- |
| **$\le$ 25th Percentile** | Hyper-Consistent / Highly Focused execution | Pinprick Star | `3.5px` |
| **> 25th to $\le$ 50th** | Stable, typical baseline performance | Standard Star | `5.0px` |
| **> 50th to $\le$ 75th** | Drifting focus or periodic attention lapses | Large Star | `7.0px` |
| **> 75th Percentile** | Highly variable or inconsistent response patterns | Diffuse Nebula | `9.5px` |

### Centroid Calculation 
Centroids represent the **mathematical expected average performance** for specific device cohorts. 

The data processing script isolates trials by game type and aggregates them by the selected hardware feature, collapsing thousands of individual data points into a single mean coordinate $(\bar{X}, \bar{Y}, \bar{Z})$:

1.  **Full Hardware Profile:** Groups trials sharing the exact combination of system memory and graphics architecture (e.g., `128GB_Apple`).
2.  **Pure Browser Engine:** Groups trials strictly by the browser rendering engine (`Safari`, `Chrome`, `Firefox`).
3.  **Pure Graphics Architecture:** Groups trials strictly by the system's GPU brand (or software based renderer (Google SwiftShader)).

Each white centroid tracked on the dashboard also logs a `Cluster_Size` (displayed as **Mass Size** on hover), which records the absolute volume of individual user trials pulled into that specific hardware profile's centroid.


