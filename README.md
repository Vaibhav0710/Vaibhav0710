<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:58a6ff&height=220&section=header&text=Vaibhav%20Jain&fontSize=60&fontColor=58a6ff&fontAlignY=35&desc=Backend%20Engineer%20%E2%80%A2%20Java%20%E2%80%A2%20Spring%20Boot%20%E2%80%A2%20Event-Driven%20Systems&descSize=18&descColor=8b949e&descAlignY=55&animation=fadeIn" width="100%"/>

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=22&duration=3000&pause=1000&color=58A6FF&center=true&vCenter=true&repeat=true&width=650&height=40&lines=Building+backends+that+don't+fall+over;Kafka+%E2%80%A2+Redis+%E2%80%A2+Spring+Cloud+%E2%80%A2+PostgreSQL;Every+vote+SHA-256+chained+to+the+last+one;Mechanical+engineer+turned+backend+engineer" alt="Typing SVG" /></a>

<br/>

[![Portfolio](https://img.shields.io/badge/Portfolio-0d1117?style=for-the-badge&logo=vercel&logoColor=58a6ff)](https://vaibhavjain-portfolio.vercel.app/)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0d1117?style=for-the-badge&logo=linkedin&logoColor=58a6ff)](https://www.linkedin.com/in/-vaibhavjain/)
[![Resume](https://img.shields.io/badge/Resume-0d1117?style=for-the-badge&logo=googledrive&logoColor=58a6ff)](https://drive.google.com/file/d/1UZ2y_ER-wKaBP7KIc2PIHicbERs4zSWQ/view?usp=sharing)
[![Email](https://img.shields.io/badge/Email-0d1117?style=for-the-badge&logo=gmail&logoColor=58a6ff)](mailto:vaibhavjain7171@gmail.com)
[![Profile Views](https://komarev.com/ghpvc/?username=Vaibhav0710&style=for-the-badge&color=58a6ff&labelColor=0d1117&label=VIEWS)](https://github.com/Vaibhav0710)

</div>

---

## `$ whoami`

```java
@Service
public class VaibhavJain implements BackendEngineer {

    private final String role     = "Junior Software Developer @ IntelligentDX";
    private final String location = "Pune, India 🇮🇳";
    private final String[] stack  = { "Java", "Spring Boot", "Kafka", "Redis", "PostgreSQL", "GCP Pub/Sub" };

    @Override
    public String atWork() {
        return "Redis caching that cut request latency by 40%, and a move from a monolith to events on Pub/Sub + Kafka";
    }

    @Override
    public String sideQuest() {
        return "A tamper-evident online voting platform: 6 Spring Boot services, every vote hash-chained";
    }

    @Override
    public String origin() {
        return "B.E. Mechanical → PG-DAC @ Sunbeam Pune → CS50x & CS50P (Harvard)";
    }
}
```

---

## ⚙️ &nbsp;Work highlights

| | What I shipped at **IntelligentDX** |
|:-:|:--|
| ⚡ | Built an appointment-rescheduling API that handles **12,000+ transactions a month** with a **99.9%** success rate |
| 🧠 | Designed a **Redis** caching layer that cut end-to-end request latency by **40%** |
| 📦 | Led the migration of **4,000+ business rules** from legacy storage to a central, high-availability Redis instance |
| 🔀 | Moved monolithic processing to an **event-driven** design on **GCP Pub/Sub** and **Kafka** |

---

## 🗳️ &nbsp;Flagship project: Blockchain-Inspired Voting System

> An online election platform where **no single service can quietly change a result**. Each vote stores the SHA-256 hash of the vote before it, so editing or deleting any row breaks the chain, and anyone can verify it through a public endpoint.

```mermaid
flowchart LR
    C([Client]) --> GW["API Gateway<br/>Spring Cloud Gateway · Redis rate limiter"]

    GW --> US["User Service<br/>JWT · BCrypt · RBAC"]
    GW --> CS["Candidate Service<br/>lifecycle · soft delete"]
    GW --> VS["Voting Service<br/>SHA-256 hash chain"]
    GW --> RS["Result Service<br/>live SSE stream"]

    VS -- Feign --> CS
    CS -- "candidate.*" --> K{{Apache Kafka}}
    VS -- "vote.cast" --> K
    K -- "vote.cast" --> RS

    US --> P1[(PostgreSQL)]
    CS --> P2[(PostgreSQL)]
    VS --> P3[(PostgreSQL)]
    VS --> R[(Redis)]
    RS --> R

    EU["Eureka<br/>service discovery"] -.- GW
```

<table>
<tr>
<td width="50%" valign="top">

**🔗 How the chain works**

```java
String prevHash = lastVoteOpt
        .map(Vote::getVoteHash)
        .orElse("GENESIS");

String newHash = hashingService.generateHash(
        userId + candidateId + electionId
        + timestampSeconds + prevHash);
```

`POST /api/v1/votes/chain/validate/{electionId}` recomputes every hash in the election and reports how many links are broken.

</td>
<td width="50%" valign="top">

**🛡️ What stops a double vote**

- A Redis `voted:` key gives a fast rejection
- A unique constraint in the database is the final guard
- Idempotency keys make retries safe
- The gateway rate-limits each user with Redis token buckets
- Results update live over **Server-Sent Events**

</td>
</tr>
</table>

| Service | Responsibility | Repo |
|:--|:--|:--:|
| 🧭 API Gateway | Routing, JWT check through User Service, Redis rate limiting | [`Voting_Api-Gateway`](https://github.com/Vaibhav0710/Voting_Api-Gateway) |
| 👤 User Service | Registration, login, BCrypt, Voter/Admin roles | [`Voting_User_Service`](https://github.com/Vaibhav0710/Voting_User_Service) |
| 🧑‍💼 Candidate Service | Candidate lifecycle (Active / Disqualified / Withdrawn), Kafka events | [`Voting_Candidate_Service`](https://github.com/Vaibhav0710/Voting_Candidate_Service) |
| 🗳️ Voting Service | Casting votes, hash chaining, verification, double-vote guard | [`Voting_Voting_Service`](https://github.com/Vaibhav0710/Voting_Voting_Service) |
| 📊 Result Service | Live counts from Kafka, kept in Redis, streamed over SSE | [`Voting_Result_Service`](https://github.com/Vaibhav0710/Voting_Result_Service) |
| 📡 Eureka Server | Service discovery | [`Voting_Eureka_Server`](https://github.com/Vaibhav0710/Voting_Eureka_Server) |

<div align="center">

**Java 17 · Spring Boot 3.3 · Spring Cloud 2023 · Kafka · Redis · PostgreSQL · OpenFeign · JJWT** &nbsp;→&nbsp; [**Voting_System**](https://github.com/Vaibhav0710/Voting_System)

</div>

---

## 🧰 &nbsp;More things I've built

<table>
<tr>
<td width="50%" valign="top">

### 🌐 [Portfolio](https://github.com/Vaibhav0710/Portfolio)
My personal site, with GSAP scroll animations, Lenis smooth scrolling and a working contact form.
<br/><sub>`Next.js 16` `React 19` `Tailwind v4` `TypeScript` `GSAP`</sub>
<br/>[**→ Live site**](https://vaibhavjain-portfolio.vercel.app/)

</td>
<td width="50%" valign="top">

### 📦 [Courier Management System](https://github.com/Vaibhav0710/Courier-management-system)
A full-stack delivery platform with separate Admin, Customer and Delivery-Partner portals, JWT login, Swagger API docs and a contact form.
<br/><sub>`Spring Boot 3.4` `Java 21` `Spring Security` `React 19` `MUI` `MySQL`</sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🚗 [Rent-A-Car](https://github.com/Vaibhav0710/Rent_A_Car)
A car-rental system with entity, DAO and service layers. Admins manage the fleet and bookings; customers register and book.
<br/><sub>`Java 17` `JDBC` `MySQL` `Maven`</sub>

</td>
<td width="50%" valign="top">

### 👥 [User Management REST API](https://github.com/Vaibhav0710/Backend-Developer-Intern-Assignment-Submission-Details)
A backend internship assignment: a CRUD API with routes, controllers and config kept apart, plus input validation and error handling.
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
My final-year engineering project: an IoT robot that monitors crop health and detects leaf disease with computer vision.
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
[![CS50x](https://img.shields.io/badge/Harvard_CS50x-0d1117?style=for-the-badge&logo=harvard&logoColor=A51C30)](https://github.com/Vaibhav0710/CS50X)
[![CS50P](https://img.shields.io/badge/Harvard_CS50P-0d1117?style=for-the-badge&logo=python&logoColor=3776AB)](https://github.com/Vaibhav0710/CS50P)

<sub>Solutions are written in Java and sync automatically from LeetCode and TUF+.</sub>

</div>

---

## 🛠️ &nbsp;Tech arsenal

<div align="center">

<img src="https://skillicons.dev/icons?i=java,spring,py,js,ts,cpp,c&theme=dark" alt="Languages" />
<br/><br/>
<img src="https://skillicons.dev/icons?i=postgres,mysql,redis,docker,gcp,maven&theme=dark" alt="Data and infrastructure" />
<br/><br/>
<img src="https://skillicons.dev/icons?i=react,nextjs,tailwind,html,css&theme=dark" alt="Frontend" />
<br/><br/>
<img src="https://skillicons.dev/icons?i=git,github,postman,idea,vscode,linux&theme=dark" alt="Tools" />

<br/><br/>

![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)
![Spring Cloud](https://img.shields.io/badge/Spring_Cloud-6DB33F?style=flat-square&logo=spring&logoColor=white)
![Spring Security](https://img.shields.io/badge/Spring_Security-6DB33F?style=flat-square&logo=springsecurity&logoColor=white)
![Hibernate](https://img.shields.io/badge/Hibernate-59666C?style=flat-square&logo=hibernate&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![GCP Pub/Sub](https://img.shields.io/badge/GCP_Pub%2FSub-4285F4?style=flat-square&logo=googlecloud&logoColor=white)
![OpenFeign](https://img.shields.io/badge/OpenFeign-6DB33F?style=flat-square&logo=spring&logoColor=white)
![Swagger](https://img.shields.io/badge/OpenAPI-85EA2D?style=flat-square&logo=swagger&logoColor=black)

</div>

---

## 🔭 &nbsp;Next on the roadmap

```diff
+ Resilience4j circuit breakers between the voting services
+ Prometheus + Grafana dashboards for every service
+ Docker images and Kubernetes manifests for the voting platform
+ Deeper system design: consistency, partitioning, back-pressure
```

---

## 📊 &nbsp;GitHub analytics

<div align="center">

<img height="170" src="https://github-readme-stats-sigma-five.vercel.app/api?username=Vaibhav0710&show_icons=true&theme=github_dark&bg_color=0d1117&border_color=30363d&title_color=58a6ff&icon_color=58a6ff&text_color=c9d1d9&count_private=true&include_all_commits=true" alt="GitHub stats" />
<img height="170" src="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username=Vaibhav0710&layout=compact&theme=github_dark&bg_color=0d1117&border_color=30363d&title_color=58a6ff&text_color=c9d1d9&langs_count=8" alt="Top languages" />

<img src="https://streak-stats.demolab.com/?user=Vaibhav0710&theme=github-dark-blue&background=0d1117&border=30363d&stroke=58a6ff&ring=58a6ff&fire=e3b341&currStreakLabel=58a6ff&sideLabels=8b949e&currStreakNum=c9d1d9&sideNums=c9d1d9&dates=8b949e" alt="GitHub streak" />

<img width="100%" src="https://github-readme-activity-graph.vercel.app/graph?username=Vaibhav0710&bg_color=0d1117&color=58a6ff&line=58a6ff&point=e3b341&area=true&area_color=58a6ff&hide_border=true" alt="Contribution activity graph" />

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
[Say hi →](mailto:vaibhavjain7171@gmail.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:161b22,100:58a6ff&height=120&section=footer" width="100%"/>

</div>
