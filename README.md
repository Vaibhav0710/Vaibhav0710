<a href="https://vaibhavjain-portfolio.vercel.app/"><img src="assets/hero.svg" width="100%" alt="Vaibhav Jain — Backend Developer. Booking & scheduling APIs on Google Cloud for healthtech. Junior Software Developer @ IntelligentDX, Pune, India."/></a>

<p align="center">
  <a href="https://vaibhavjain-portfolio.vercel.app/"><img src="https://img.shields.io/badge/Portfolio-0b1220?style=for-the-badge&logo=vercel&logoColor=22d3ee" alt="Portfolio"/></a>
  <a href="https://www.linkedin.com/in/-vaibhavjain/"><img src="https://img.shields.io/badge/LinkedIn-0b1220?style=for-the-badge&logo=linkedin&logoColor=a78bfa" alt="LinkedIn"/></a>
  <a href="https://vaibhavjain-portfolio.vercel.app/Vaibhav_Jain_Java_Backend_Developer_CV.pdf"><img src="https://img.shields.io/badge/Resume-0b1220?style=for-the-badge&logo=adobeacrobatreader&logoColor=f472b6" alt="Resume"/></a>
  <a href="mailto:vaibhav.jain.careers@gmail.com"><img src="https://img.shields.io/badge/Email-0b1220?style=for-the-badge&logo=gmail&logoColor=34d399" alt="Email"/></a>
  <img src="https://komarev.com/ghpvc/?username=Vaibhav0710&style=for-the-badge&color=0b1220&labelColor=0b1220&label=%F0%9F%91%80%20VIEWS" alt="Profile views"/>
</p>

<br/>

## ⚡ What I ship at IntelligentDX

<sub>Healthtech software for eye-care practices · intern from Apr 2025, full-time since Nov 2025</sub>

<img src="assets/impact.svg" width="100%" alt="Impact: treatment-plan booking across 15 parallel lanes, live since Sep 2026; cancel and reschedule with HTTP 207; slot search cut from 2.7–3.6s to 1.7–2.5s; background sync for 213 providers × 111 locations × 70 visit types; AI rule generation 27–31% cheaper per rule; 10 read paths across 5 C#/.NET services migrated from MongoDB to PostgreSQL in ~8 weeks."/>

<details>
<summary><b>Read the details</b></summary>
<br/>

- **Treatment-plan booking API.** Books every visit of a multi-appointment plan across up to 15 parallel lanes, with atomic slot reservation, one audit row per appointment and 200/207/422 responses. In production since September 2026.
- **Cancel & reschedule APIs.** On an EHR with no native reschedule: book the new slot first, retry at timed offsets, return HTTP 207 on partial success, full audit trail.
- **Background sync.** Cloud Scheduler → Cloud Run Jobs → PostgreSQL for 213 providers × 111 locations × 70 visit types, replacing slow or timing-out external calls with indexed database reads.
- **Faster slot search.** About 2.7–3.6 s down to 1.7–2.5 s with a concurrent pager; moved scheduling APIs to an EHR's FHIR R4 API with unchanged API contracts.
- **AI rule generation.** A platform around Claude with validation gates and a repair loop; prompt caching cut cost per generated rule by about 27–31%.
- **Internship migration.** 10 API read paths across 5 C#/.NET microservices moved from MongoDB to PostgreSQL in about 8 weeks; 9 reached production with identical responses.

</details>

<br/>

## 🗳️ Flagship project

<a href="https://github.com/Vaibhav0710/Voting_System"><img src="assets/voting.svg" width="100%" alt="Blockchain-Inspired Voting System: each vote stores the SHA-256 hash of the previous vote, so editing a row breaks the chain and the validator finds the broken link. Six Spring Boot services: API Gateway, User, Candidate, Voting, Result, Eureka."/></a>

<details>
<summary><b>Architecture</b></summary>
<br/>

```mermaid
flowchart LR
    C([Client]) --> GW["API Gateway<br/>rate limiter · circuit breakers"]
    GW --> US["User Service<br/>JWT · BCrypt · RBAC"]
    GW --> CS["Candidate Service<br/>lifecycle · Redis cache"]
    GW --> VS["Voting Service<br/>SHA-256 hash chain"]
    GW --> RS["Result Service<br/>live SSE stream"]
    VS -- "Feign + Resilience4j" --> CS
    CS -- "candidate.*" --> K{{Apache Kafka}}
    VS -- "vote.cast" --> K
    K -- "vote.cast" --> RS
    US & CS & VS --> PG[("PostgreSQL<br/>schema per service")]
    GW & CS & VS & RS --> R[(Redis)]
    EU["Eureka"] -.- GW
```

</details>

<details>
<summary><b>How the hash chain works</b></summary>
<br/>

```java
// one row per election, SELECT … FOR UPDATE
ElectionChainHead head = chainHeadService.lockHead(electionId);

Vote vote = Vote.builder()
        .prevHash(head.getLastHash())   // "GENESIS" for the first vote
        /* user, candidate, election, time */
        .build();

// SHA-256(userId + candidateId + electionId + epochSeconds + prevHash)
vote.setVoteHash(voteHasher.computeHash(vote));
head.setLastHash(vote.getVoteHash());
```

Locking the chain head makes concurrent votes link one after another. `POST /api/v1/votes/chain/validate/{electionId}` (admin only) recomputes every hash and reports how many links are broken.

**Double votes are stopped by:** a Redis `voted:` key for fast rejection · a unique DB constraint as the final guard · idempotency keys for safe retries · per-user Redis token-bucket rate limits · Result Service skipping vote ids it has already counted.

**Beyond the core:** Resilience4j circuit breakers with Redis fallbacks · Prometheus + Grafana, Zipkin, ELK · Docker Compose and Kubernetes (Kustomize, ingress) · JUnit, Testcontainers, JaCoCo, end-to-end and chaos scripts, Gatling load tests.

</details>

<details>
<summary><b>Service repos</b></summary>
<br/>

| Service | Responsibility | Repo |
|:--|:--|:--:|
| 🧭 API Gateway | Routing, JWT check, role checks, CORS, Redis rate limiting, circuit breakers | [`Voting_Api-Gateway`](https://github.com/Vaibhav0710/Voting_Api-Gateway) |
| 👤 User | Registration, login, BCrypt, Voter/Admin roles | [`Voting_User_Service`](https://github.com/Vaibhav0710/Voting_User_Service) |
| 🧑‍💼 Candidate | Lifecycle (Active / Disqualified / Withdrawn), Redis cache, Kafka events after commit | [`Voting_Candidate_Service`](https://github.com/Vaibhav0710/Voting_Candidate_Service) |
| 🗳️ Voting | Casting votes, hash chaining, verification, double-vote guard | [`Voting_Voting_Service`](https://github.com/Vaibhav0710/Voting_Voting_Service) |
| 📊 Result | Live counts from Kafka, kept in Redis, streamed over SSE | [`Voting_Result_Service`](https://github.com/Vaibhav0710/Voting_Result_Service) |
| 📡 Eureka | Service discovery | [`Voting_Eureka_Server`](https://github.com/Vaibhav0710/Voting_Eureka_Server) |

</details>

<br/>

## 🧰 More builds

<p align="center">
  <a href="https://github.com/Vaibhav0710/Courier-management-system"><img src="assets/project-courier.svg" width="49%" alt="Courier Management: full-stack delivery platform — Spring Boot 3.4, JPA, MySQL, React"/></a>
  <a href="https://github.com/Vaibhav0710/Portfolio"><img src="assets/project-portfolio.svg" width="49%" alt="Portfolio: personal site on Vercel — Next.js, TypeScript, Tailwind"/></a>
</p>
<p align="center">
  <a href="https://github.com/Vaibhav0710/Rent_A_Car"><img src="assets/project-rentacar.svg" width="49%" alt="Rent-A-Car: layered car-rental system — Java 17, JDBC, MySQL"/></a>
  <a href="https://github.com/Vaibhav0710/Backend-Developer-Intern-Assignment-Submission-Details"><img src="assets/project-userapi.svg" width="49%" alt="User Management API: modular CRUD REST API — Node.js, Express, MySQL"/></a>
</p>
<p align="center">
  <a href="https://github.com/Vaibhav0710/DesignDevelopmentOfAutonomousFarmingWithPlanthealthIndicationSystem"><img src="assets/project-farmbot.svg" width="49%" alt="Autonomous Farming Robot: IoT crop and soil monitoring — ESP32, OpenCV, Python"/></a>
  <a href="https://github.com/Vaibhav0710/Pizza-Shop"><img src="assets/project-pizza.svg" width="49%" alt="Pizza Shop: console ordering system — Core Java, JDBC, MySQL"/></a>
</p>

<p align="center"><sub>Also: <a href="https://github.com/Vaibhav0710/Sudoku_Game">🧩 Sudoku</a> (JavaFX) · <a href="https://github.com/Vaibhav0710/Movie-Finder">🎬 Movie Finder</a> (React)</sub></p>

<br/>

## 🛠️ Toolbox

<p align="center">
  <img src="https://skillicons.dev/icons?i=py,flask,nodejs,express,cs,dotnet,postgres,redis,gcp&theme=dark&perline=9" alt="At work: Python, Flask, Node.js, Express, C#, .NET, PostgreSQL, Redis, Google Cloud"/><br/>
  <sub><b>AT WORK</b></sub>
</p>
<p align="center">
  <img src="https://skillicons.dev/icons?i=java,spring,kafka,mysql,mongodb,docker,kubernetes,prometheus,grafana&theme=dark&perline=9" alt="In projects: Java, Spring, Kafka, MySQL, MongoDB, Docker, Kubernetes, Prometheus, Grafana"/><br/>
  <sub><b>IN PROJECTS</b></sub>
</p>

<br/>

## 🧠 Always learning

<p align="center">
  <a href="https://github.com/Vaibhav0710/Leetcode-solution"><img src="https://img.shields.io/badge/LeetCode_Solutions-0b1220?style=for-the-badge&logo=leetcode&logoColor=FFA116" alt="LeetCode"/></a>
  <a href="https://github.com/Vaibhav0710/Daily_DSA"><img src="https://img.shields.io/badge/90--Day_DSA_Plan-0b1220?style=for-the-badge&logo=openjdk&logoColor=22d3ee" alt="Daily DSA"/></a>
  <a href="https://github.com/Vaibhav0710/CS50X"><img src="https://img.shields.io/badge/CS50x-0b1220?style=for-the-badge&logo=harvard&logoColor=f472b6" alt="CS50x"/></a>
  <a href="https://github.com/Vaibhav0710/CS50P"><img src="https://img.shields.io/badge/CS50P-0b1220?style=for-the-badge&logo=python&logoColor=a78bfa" alt="CS50P"/></a>
  <br/>
  <sub>Java Full Stack LIVE (Spark 2.0) · Alpha: DSA with Java (Apna College) · Google Cloud Bootcamp (GeeksforGeeks) · LeetCode 100 Days Badge 2024</sub>
</p>

<br/>

## 📈 Activity

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-night-view.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-green-animate.svg" />
  <img width="100%" alt="3D contribution calendar with totals and languages" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-night-view.svg" />
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake.svg" />
  <img width="100%" alt="Snake eating my contribution graph" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake-dark.svg" />
</picture>

<br/><br/>

<a href="mailto:vaibhav.jain.careers@gmail.com"><img src="assets/footer.svg" width="100%" alt="Let's build something reliable — vaibhav.jain.careers@gmail.com"/></a>

<!-- Graphics in assets/ are generated by scripts/build_assets.py. Edit the text there and re-run it. -->
