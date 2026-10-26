<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:58a6ff&height=220&section=header&text=Vaibhav%20Jain&fontSize=60&fontColor=58a6ff&fontAlignY=35&desc=Backend%20Developer%20%E2%80%A2%20Booking%20%26%20Scheduling%20APIs%20%E2%80%A2%20Google%20Cloud&descSize=18&descColor=8b949e&descAlignY=55&animation=fadeIn" width="100%"/>

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=3000&pause=1000&color=58A6FF&center=true&vCenter=true&repeat=true&width=650&height=40&lines=Booking+%26+scheduling+APIs+on+Google+Cloud;Python+%E2%80%A2+Node.js+%E2%80%A2+C%23%2F.NET+at+work;Java+%E2%80%A2+Spring+Boot+%E2%80%A2+Kafka+in+projects;Every+vote+SHA-256+chained+to+the+last+one;Mechanical+engineer+turned+backend+developer" alt="Typing SVG" /></a>

<br/>

[![Portfolio](https://img.shields.io/badge/Portfolio-0d1117?style=for-the-badge&logo=vercel&logoColor=58a6ff)](https://vaibhavjain-portfolio.vercel.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0d1117?style=for-the-badge&logo=linkedin&logoColor=58a6ff)](https://www.linkedin.com/in/-vaibhavjain/)
[![Resume](https://img.shields.io/badge/Resume-0d1117?style=for-the-badge&logo=adobeacrobatreader&logoColor=58a6ff)](https://vaibhavjain-portfolio.vercel.app/Vaibhav_Jain_Java_Backend_Developer_CV.pdf)
[![Email](https://img.shields.io/badge/Email-0d1117?style=for-the-badge&logo=gmail&logoColor=58a6ff)](mailto:vaibhav.jain.careers@gmail.com)
[![Profile Views](https://komarev.com/ghpvc/?username=Vaibhav0710&style=for-the-badge&color=58a6ff&labelColor=0d1117&label=VIEWS)](https://github.com/Vaibhav0710)

</div>

---

## `$ whoami`

```java
@Service
public class VaibhavJain implements BackendDeveloper {

    private final String role       = "Junior Software Developer @ IntelligentDX"; // healthtech software for eye-care practices
    private final String location   = "Pune, India 🇮🇳";
    private final String experience = "1.5 years: intern from Apr 2025, full-time since Nov 2025";

    private final String[] workStack    = { "Python (Flask)", "Node.js (Express)", "C#/.NET", "PostgreSQL", "Redis", "BigQuery", "Google Cloud" };
    private final String[] projectStack = { "Java", "Spring Boot", "Spring Cloud", "Kafka", "Docker", "Kubernetes" };

    @Override
    public String atWork() {
        return "Booking and scheduling APIs on Google Cloud, from treatment-plan booking to Cloud Run sync jobs";
    }

    @Override
    public String sideQuest() {
        return "A tamper-evident online voting platform: 6 Spring Boot services, every vote hash-chained";
    }

    @Override
    public String origin() {
        return "B.E. Mechanical (MESCOE Pune, 2019–2023) → PG-DAC (C-DAC) at Sunbeam Pune";
    }
}
```

---

## ⚙️ &nbsp;Work highlights

| | At **IntelligentDX** · healthtech software for eye-care practices |
|:-:|:--|
| 📅 | Built a **treatment-plan booking API** that books every visit of a multi-appointment plan across up to **15 parallel lanes**, with atomic slot reservation, one audit row per appointment and 200/207/422 responses. In production since **September 2026**. |
| 🔁 | Built **cancel and reschedule APIs** on an EHR with no native reschedule: book the new slot first, retry at timed offsets, return **HTTP 207** on partial success, full audit trail. |
| ⏱️ | Designed **background sync** (Cloud Scheduler → Cloud Run Jobs → PostgreSQL) for **213 providers × 111 locations × 70 visit types**, replacing slow or timing-out external calls with indexed database reads. |
| ⚡ | Cut the **slot-search API** from about **2.7–3.6 s to 1.7–2.5 s** with a concurrent pager, and moved scheduling APIs to an EHR's **FHIR R4** API with unchanged API contracts. |
| 🤖 | Designed an **AI rule-generation platform** around Claude with validation gates and a repair loop; prompt caching cut cost per generated rule by about **27–31%**. |
| 🧳 | *Internship:* migrated **10 API read paths** across **5 C#/.NET microservices** from MongoDB to PostgreSQL in about **8 weeks**; 9 reached production with identical responses. |

---

## 🗳️ &nbsp;Flagship project: Blockchain-Inspired Voting System

> An online election platform built so that **tampering with stored votes is detectable**. Each vote stores the SHA-256 hash of the vote before it, so editing or deleting any row breaks the chain, and a verification endpoint can find the break.

```mermaid
flowchart LR
    C([Client]) --> GW["API Gateway<br/>rate limiter · circuit breakers"]

    GW --> US["User Service<br/>JWT · BCrypt · RBAC"]
    GW --> CS["Candidate Service<br/>lifecycle · Redis read cache"]
    GW --> VS["Voting Service<br/>SHA-256 hash chain"]
    GW --> RS["Result Service<br/>live SSE stream"]

    VS -- "Feign + Resilience4j" --> CS
    CS -- "candidate.*" --> K{{Apache Kafka}}
    VS -- "vote.cast" --> K
    K -- "vote.cast" --> RS

    US & CS & VS --> PG[("PostgreSQL<br/>one schema per service")]
    GW & CS & VS & RS --> R[(Redis)]

    EU["Eureka<br/>service discovery"] -.- GW
```

<table>
<tr>
<td width="50%" valign="top">

**🔗 How the chain works**

```java
// one row per election, SELECT … FOR UPDATE
ElectionChainHead head =
        chainHeadService.lockHead(electionId);

Vote vote = Vote.builder()
        .prevHash(head.getLastHash()) // "GENESIS" first
        /* user, candidate, election, time */
        .build();

// SHA-256(userId + candidateId + electionId
//         + epochSeconds + prevHash)
vote.setVoteHash(voteHasher.computeHash(vote));
head.setLastHash(vote.getVoteHash());
```

Locking the election's chain head makes concurrent votes link one after another. `POST /api/v1/votes/chain/validate/{electionId}` (admin only) recomputes every hash in the election and reports how many links are broken.

</td>
<td width="50%" valign="top">

**🛡️ What stops a double vote**

- A Redis `voted:` key gives a fast rejection
- A unique constraint in the database is the final guard
- Idempotency keys make retries safe
- The gateway rate-limits each user with Redis token buckets
- Result Service skips vote ids it has already counted, so each vote counts once

</td>
</tr>
</table>

| Service | Responsibility | Repo |
|:--|:--|:--:|
| 🧭 API Gateway | Routing, JWT check through User Service, role checks, CORS, Redis rate limiting, circuit breakers with fallbacks | [`Voting_Api-Gateway`](https://github.com/Vaibhav0710/Voting_Api-Gateway) |
| 👤 User Service | Registration, login, BCrypt, Voter/Admin roles | [`Voting_User_Service`](https://github.com/Vaibhav0710/Voting_User_Service) |
| 🧑‍💼 Candidate Service | Candidate lifecycle (Active / Disqualified / Withdrawn), Redis read cache, Kafka events sent after commit | [`Voting_Candidate_Service`](https://github.com/Vaibhav0710/Voting_Candidate_Service) |
| 🗳️ Voting Service | Casting votes, hash chaining, verification, double-vote guard | [`Voting_Voting_Service`](https://github.com/Vaibhav0710/Voting_Voting_Service) |
| 📊 Result Service | Live counts from Kafka, kept in Redis, streamed over SSE | [`Voting_Result_Service`](https://github.com/Vaibhav0710/Voting_Result_Service) |
| 📡 Eureka Server | Service discovery | [`Voting_Eureka_Server`](https://github.com/Vaibhav0710/Voting_Eureka_Server) |

**Beyond the core features**

| | |
|:-:|:--|
| 🛡️ | **Resilience:** Resilience4j circuit breakers on every gateway route. If Candidate Service is down, Voting Service falls back to a Redis cache of candidate statuses it has already seen. |
| 📈 | **Observability:** Prometheus metrics, a Grafana dashboard, Zipkin tracing and JSON logs shipped to ELK. |
| 🐳 | **Deployment:** a Dockerfile per service, a full Docker Compose stack, and Kubernetes manifests (Kustomize, ingress). |
| 🧪 | **Testing:** JUnit tests in every service, a Testcontainers PostgreSQL test, JaCoCo coverage, scripted end-to-end and chaos runs, and Gatling load tests. |

<div align="center">

**Java 17 · Spring Boot 3.3 · Spring Cloud 2023 · Kafka · Redis · PostgreSQL · OpenFeign · Resilience4j · JJWT · Docker · Kubernetes** &nbsp;→&nbsp; [**Voting_System**](https://github.com/Vaibhav0710/Voting_System)

</div>

---

## 🧰 &nbsp;More things I've built

<table>
<tr>
<td width="50%" valign="top">

### 🌐 [Portfolio](https://github.com/Vaibhav0710/Portfolio)
My personal portfolio site, deployed on Vercel.
<br/><sub>`Next.js` `TypeScript` `Tailwind` `Vercel`</sub>
<br/>[**→ Live site**](https://vaibhavjain-portfolio.vercel.app/)

</td>
<td width="50%" valign="top">

### 📦 [Courier Management System](https://github.com/Vaibhav0710/Courier-management-system)
A full-stack delivery platform with separate Admin, Customer and Delivery-Partner modules, JWT login, OpenAPI docs and a contact form.
<br/><sub>`Java 21` `Spring Boot 3.4` `Spring Data JPA` `Spring Security + JWT` `springdoc OpenAPI` `MySQL` `React`</sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🚗 [Rent-A-Car](https://github.com/Vaibhav0710/Rent_A_Car)
A console car-rental system with entity, DAO and service layers. Admins manage the fleet and bookings; customers register and book.
<br/><sub>`Java 17` `JDBC` `MySQL` `Maven`</sub>

</td>
<td width="50%" valign="top">

### 👥 [User Management REST API](https://github.com/Vaibhav0710/Backend-Developer-Intern-Assignment-Submission-Details)
A backend internship assignment: a CRUD REST API with routes, controller, model and DB config in separate modules, required-field checks and 400/404/500 error responses.
<br/><sub>`Node.js` `Express` `MySQL`</sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🍕 [Pizza Shop](https://github.com/Vaibhav0710/Pizza-Shop)
A console ordering system with login, a categorised menu, a cart and an admin view of orders.
<br/><sub>`Core Java` `JDBC` `MySQL`</sub>

</td>
<td width="50%" valign="top">

### 🌱 [Autonomous Farming Robot](https://github.com/Vaibhav0710/DesignDevelopmentOfAutonomousFarmingWithPlanthealthIndicationSystem)
Final-year B.E. project: an IoT robot that monitors crop and soil health and detects leaf disease with image processing.
<br/><sub>`ESP32` `Arduino` `OpenCV` `Python` `IoT sensors`</sub>

</td>
</tr>
</table>

<details>
<summary><b>🎮 &nbsp;Games and early builds</b> (click to expand)</summary>
<br/>

| Project | What it is | Stack |
|:--|:--|:--|
| 🧩 [Sudoku](https://github.com/Vaibhav0710/Sudoku_Game) | A desktop Sudoku with a puzzle generator, saved progress, and separate domain, persistence and UI layers | `Java` `JavaFX` |
| 🎬 [Movie Finder](https://github.com/Vaibhav0710/Movie-Finder) | Search movies and view details from the OMDB API | `React` `JavaScript` |

</details>

---

## 🧠 &nbsp;Problem-solving

<div align="center">

[![LeetCode](https://img.shields.io/badge/LeetCode_Solutions-0d1117?style=for-the-badge&logo=leetcode&logoColor=FFA116)](https://github.com/Vaibhav0710/Leetcode-solution)
[![Daily DSA](https://img.shields.io/badge/90--Day_DSA_Plan-0d1117?style=for-the-badge&logo=openjdk&logoColor=58a6ff)](https://github.com/Vaibhav0710/Daily_DSA)
[![CS50x](https://img.shields.io/badge/CS50x_repo-0d1117?style=for-the-badge&logo=github&logoColor=58a6ff)](https://github.com/Vaibhav0710/CS50X)
[![CS50P](https://img.shields.io/badge/CS50P_repo-0d1117?style=for-the-badge&logo=python&logoColor=3776AB)](https://github.com/Vaibhav0710/CS50P)

<sub>LeetCode and TUF+ solutions sync automatically through LeetHub and TUFHub.</sub>

**📜 Certifications**<br/>
<sub>Java Full Stack LIVE Course (Spark 2.0) · Alpha: DSA with Java (Apna College) · Google Cloud Bootcamp (GeeksforGeeks) · LeetCode 100 Days Badge 2024</sub>

</div>

---

## 🛠️ &nbsp;Tech arsenal

<div align="center">

<img src="https://skillicons.dev/icons?i=java,spring,py,nodejs,cs&theme=dark" alt="Languages and frameworks" />
<br/><br/>
<img src="https://skillicons.dev/icons?i=postgres,mysql,redis,mongodb,docker,kubernetes,gcp,maven,kafka,prometheus,grafana&theme=dark" alt="Data and infrastructure" />
<br/><br/>
<img src="https://skillicons.dev/icons?i=git,github,linux&theme=dark" alt="Tools" />

<br/><br/>

![Spring Cloud](https://img.shields.io/badge/Spring_Cloud-6DB33F?style=flat-square&logo=spring&logoColor=white)
![Spring Security](https://img.shields.io/badge/Spring_Security-6DB33F?style=flat-square&logo=springsecurity&logoColor=white)
![Spring Data JPA](https://img.shields.io/badge/Spring_Data_JPA-6DB33F?style=flat-square&logo=spring&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![OpenFeign](https://img.shields.io/badge/OpenFeign-6DB33F?style=flat-square&logo=spring&logoColor=white)
![OpenAPI](https://img.shields.io/badge/OpenAPI-85EA2D?style=flat-square&logo=swagger&logoColor=black)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka_%28projects%29-231F20?style=flat-square&logo=apachekafka&logoColor=white)
![Resilience4j](https://img.shields.io/badge/Resilience4j_%28projects%29-0d1117?style=flat-square)

<sub>At work: Python (Flask), Node.js (Express), C#/.NET, PostgreSQL, Redis, BigQuery, Google Cloud.<br/>In projects and training: Java, Spring Boot, Spring Cloud, Kafka, Resilience4j, Docker, Kubernetes, Prometheus, Grafana.</sub>

</div>

---

## 🔭 &nbsp;Next on the roadmap

```diff
+ Finish the 10,000-vote load run (p95 under 500 ms, zero errors) and publish the results
+ Deeper system design: consistency, partitioning, back-pressure
```

---

## 📊 &nbsp;GitHub analytics

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-night-view.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-green-animate.svg" />
  <img width="100%" alt="3D contribution calendar with contribution totals and languages" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-night-view.svg" />
</picture>

<img src="https://streak-stats.demolab.com/?user=Vaibhav0710&theme=github-dark-blue&background=0d1117&border=30363d&stroke=58a6ff&ring=58a6ff&fire=e3b341&currStreakLabel=58a6ff&sideLabels=8b949e&currStreakNum=c9d1d9&sideNums=c9d1d9&dates=8b949e" alt="GitHub streak" />

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake.svg" />
  <img alt="Snake eating my contribution graph" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake-dark.svg" />
</picture>

</div>

---

<div align="center">

### 💡 *"Make it work, make it right, make it fast" (in that order)*

**Open to conversations about backend engineering, distributed systems and interesting problems.**<br/>
[Say hi →](mailto:vaibhav.jain.careers@gmail.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:58a6ff&height=120&section=footer" width="100%"/>

</div>
