<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,55:1f6feb,100:8957e5&height=230&section=header&text=Vaibhav%20Jain&fontSize=64&fontColor=ffffff&fontAlignY=36&desc=Backend%20Developer%20%C2%B7%20Booking%20%26%20Scheduling%20APIs%20%C2%B7%20Google%20Cloud&descSize=18&descColor=e6edf3&descAlignY=57&animation=fadeIn" width="100%" alt="Vaibhav Jain, Backend Developer"/>

<a href="https://vaibhavjain-portfolio.vercel.app/"><img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=21&duration=2800&pause=900&color=58A6FF&center=true&vCenter=true&repeat=true&width=680&height=42&lines=Backend+developer+%40+IntelligentDX%2C+Pune;Booking+%26+scheduling+APIs+on+Google+Cloud;Python+%C2%B7+Node.js+%C2%B7+C%23%2F.NET+%C2%B7+PostgreSQL;Java+%C2%B7+Spring+Boot+%C2%B7+Kafka+in+side+projects;Mechanical+engineer+turned+software+developer" alt="Typing intro"/></a>

<p>
  <a href="https://vaibhavjain-portfolio.vercel.app/"><img src="https://img.shields.io/badge/Portfolio-1f6feb?style=for-the-badge&logo=vercel&logoColor=white" alt="Portfolio"/></a>
  <a href="https://www.linkedin.com/in/-vaibhavjain/"><img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/></a>
  <a href="https://vaibhavjain-portfolio.vercel.app/Vaibhav_Jain_Java_Backend_Developer_CV.pdf"><img src="https://img.shields.io/badge/Resume-8957e5?style=for-the-badge&logo=readdotcv&logoColor=white" alt="Resume"/></a>
  <a href="mailto:vaibhav.jain.careers@gmail.com"><img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email"/></a>
  <img src="https://komarev.com/ghpvc/?username=Vaibhav0710&style=for-the-badge&color=1f6feb&label=PROFILE+VIEWS" alt="Profile views"/>
</p>

</div>

## 👋 About me

- 💼 **Junior Software Developer at IntelligentDX**, healthtech software for eye-care practices (intern from Apr 2025, full-time since Nov 2025)
- ⚙️ I build **booking and scheduling APIs on Google Cloud** with Python, Node.js, C#/.NET and PostgreSQL
- ☕ On the side I build **distributed systems in Java and Spring Boot**
- 🎓 B.E. Mechanical (MESCOE Pune, 2019–2023), then PG-DAC at C-DAC (Sunbeam Pune)
- 🌱 Next up: a 10,000-vote load test for my voting system and deeper system design
- 📍 Pune, India · 📫 vaibhav.jain.careers@gmail.com

## 🚀 What I've shipped

| | Work at IntelligentDX |
|:-:|:--|
| 📅 | **Treatment-plan booking API**: books every visit of a multi-appointment plan across up to **15 parallel lanes**, with atomic slot reservation and one audit row per appointment. Live since **Sep 2026**. |
| 🔁 | **Cancel & reschedule APIs** on an EHR with no native reschedule: book the new slot first, retry at timed offsets, **HTTP 207** on partial success. |
| ⏱️ | **Background sync** (Cloud Scheduler → Cloud Run Jobs → PostgreSQL) for **213 providers × 111 locations × 70 visit types**. |
| ⚡ | **Slot search** cut from **~2.7–3.6 s to 1.7–2.5 s** with a concurrent pager; scheduling APIs moved to **FHIR R4** with unchanged contracts. |
| 🤖 | **AI rule generation** around Claude with validation gates and a repair loop; prompt caching cut cost per rule by **~27–31%**. |
| 🧳 | *Internship:* **10 read paths** across **5 C#/.NET services** moved from MongoDB to PostgreSQL in ~8 weeks; 9 reached production. |

## 🗳️ Featured project: [Blockchain-Inspired Voting System](https://github.com/Vaibhav0710/Voting_System)

> Six Spring Boot services. Every vote stores the **SHA-256 hash of the previous vote**, so editing or deleting any row breaks the chain, and an admin endpoint finds the break.

```mermaid
flowchart LR
    C([Client]) --> GW["API Gateway<br/>rate limit · circuit breakers"]
    GW --> US["User<br/>JWT · BCrypt"]
    GW --> CS["Candidate<br/>Redis cache"]
    GW --> VS["Voting<br/>SHA-256 chain"]
    GW --> RS["Result<br/>live SSE"]
    VS -- Feign + Resilience4j --> CS
    CS -- candidate.* --> K{{Kafka}}
    VS -- vote.cast --> K
    K --> RS
    US & CS & VS --> PG[(PostgreSQL)]
    GW & CS & VS & RS --> R[(Redis)]
```

<p align="center">
  <img src="https://img.shields.io/badge/Java_17-ED8B00?style=flat-square&logo=openjdk&logoColor=white"/>
  <img src="https://img.shields.io/badge/Spring_Boot_3.3-6DB33F?style=flat-square&logo=springboot&logoColor=white"/>
  <img src="https://img.shields.io/badge/Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-DC382D?style=flat-square&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Resilience4j-1f6feb?style=flat-square"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white"/>
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=flat-square&logo=kubernetes&logoColor=white"/>
</p>

<details>
<summary><b>Services and how the chain works</b></summary>
<br/>

| Service | Responsibility |
|:--|:--|
| 🧭 [API Gateway](https://github.com/Vaibhav0710/Voting_Api-Gateway) | Routing, JWT checks, Redis rate limiting, circuit breakers |
| 👤 [User](https://github.com/Vaibhav0710/Voting_User_Service) | Registration, login, BCrypt, Voter/Admin roles |
| 🧑‍💼 [Candidate](https://github.com/Vaibhav0710/Voting_Candidate_Service) | Candidate lifecycle, Redis cache, Kafka events |
| 🗳️ [Voting](https://github.com/Vaibhav0710/Voting_Voting_Service) | Casting votes, hash chaining, double-vote guard |
| 📊 [Result](https://github.com/Vaibhav0710/Voting_Result_Service) | Live counts from Kafka, streamed over SSE |
| 📡 [Eureka](https://github.com/Vaibhav0710/Voting_Eureka_Server) | Service discovery |

```java
ElectionChainHead head = chainHeadService.lockHead(electionId); // SELECT … FOR UPDATE
Vote vote = Vote.builder().prevHash(head.getLastHash()) /* "GENESIS" first */ .build();
vote.setVoteHash(voteHasher.computeHash(vote)); // SHA-256(user + candidate + election + time + prevHash)
head.setLastHash(vote.getVoteHash());
```

Also: Prometheus + Grafana, Zipkin, ELK, Docker Compose, Kubernetes (Kustomize), JUnit, Testcontainers, Gatling load tests.

</details>

## 🧰 More projects

<table>
<tr>
<td width="50%" valign="top">

**📦 [Courier Management System](https://github.com/Vaibhav0710/Courier-management-system)**<br/>
Delivery platform with Admin, Customer and Delivery-Partner modules, JWT login and OpenAPI docs.<br/>
<sub>`Spring Boot 3.4` `JPA` `MySQL` `React`</sub>

</td>
<td width="50%" valign="top">

**🌐 [Portfolio](https://github.com/Vaibhav0710/Portfolio)** · [live](https://vaibhavjain-portfolio.vercel.app/)<br/>
My personal site, deployed on Vercel.<br/>
<sub>`Next.js` `TypeScript` `Tailwind`</sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

**🚗 [Rent-A-Car](https://github.com/Vaibhav0710/Rent_A_Car)**<br/>
Car-rental system with entity, DAO and service layers.<br/>
<sub>`Java 17` `JDBC` `MySQL`</sub>

</td>
<td width="50%" valign="top">

**👥 [User Management API](https://github.com/Vaibhav0710/Backend-Developer-Intern-Assignment-Submission-Details)**<br/>
CRUD REST API with validation and 400/404/500 handling.<br/>
<sub>`Node.js` `Express` `MySQL`</sub>

</td>
</tr>
<tr>
<td width="50%" valign="top">

**🌱 [Autonomous Farming Robot](https://github.com/Vaibhav0710/DesignDevelopmentOfAutonomousFarmingWithPlanthealthIndicationSystem)**<br/>
Final-year IoT robot that monitors soil and detects leaf disease.<br/>
<sub>`ESP32` `OpenCV` `Python`</sub>

</td>
<td width="50%" valign="top">

**🍕 [Pizza Shop](https://github.com/Vaibhav0710/Pizza-Shop)** · **🧩 [Sudoku](https://github.com/Vaibhav0710/Sudoku_Game)** · **🎬 [Movie Finder](https://github.com/Vaibhav0710/Movie-Finder)**<br/>
Console ordering app, JavaFX Sudoku and an OMDB movie search.<br/>
<sub>`Core Java` `JavaFX` `React`</sub>

</td>
</tr>
</table>

## 🛠️ Tech stack

<p align="center">
  <b>At work</b><br/><br/>
  <img src="https://skillicons.dev/icons?i=py,flask,nodejs,express,cs,dotnet,postgres,redis,gcp&perline=9" alt="Python, Flask, Node.js, Express, C#, .NET, PostgreSQL, Redis, Google Cloud"/>
  <br/><br/>
  <b>Projects and tools</b><br/><br/>
  <img src="https://skillicons.dev/icons?i=java,spring,kafka,mysql,mongodb,docker,kubernetes,prometheus,grafana,git,github,linux&perline=12" alt="Java, Spring, Kafka, MySQL, MongoDB, Docker, Kubernetes, Prometheus, Grafana, Git, GitHub, Linux"/>
</p>

## 📊 GitHub stats

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/cards/github_dark/0-profile-details.svg"/>
    <img width="100%" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/cards/default/0-profile-details.svg" alt="Profile details"/>
  </picture>
</p>
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/cards/github_dark/3-stats.svg"/>
    <img width="49%" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/cards/default/3-stats.svg" alt="Stats"/>
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/cards/github_dark/2-most-commit-language.svg"/>
    <img width="49%" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/cards/default/2-most-commit-language.svg" alt="Most-committed languages"/>
  </picture>
</p>
<p align="center">
  <img src="https://streak-stats.demolab.com/?user=Vaibhav0710&theme=github-dark-blue&hide_border=true&background=0d1117&ring=1f6feb&fire=8957e5&currStreakLabel=58a6ff" alt="Streak"/>
</p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-night-view.svg"/>
  <img width="100%" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/profile-green-animate.svg" alt="3D contribution calendar"/>
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake-dark.svg"/>
  <img width="100%" src="https://raw.githubusercontent.com/Vaibhav0710/Vaibhav0710/output/github-snake.svg" alt="Snake eating my contribution graph"/>
</picture>

## 🧠 Problem solving

<p align="center">
  <a href="https://github.com/Vaibhav0710/Leetcode-solution"><img src="https://img.shields.io/badge/LeetCode_Solutions-FFA116?style=for-the-badge&logo=leetcode&logoColor=black"/></a>
  <a href="https://github.com/Vaibhav0710/Daily_DSA"><img src="https://img.shields.io/badge/90--Day_DSA-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white"/></a>
  <a href="https://github.com/Vaibhav0710/CS50X"><img src="https://img.shields.io/badge/CS50x-A51C30?style=for-the-badge&logo=harvard&logoColor=white"/></a>
  <a href="https://github.com/Vaibhav0710/CS50P"><img src="https://img.shields.io/badge/CS50P-3776AB?style=for-the-badge&logo=python&logoColor=white"/></a>
  <br/>
  <sub>📜 Java Full Stack LIVE (Spark 2.0) · Alpha: DSA with Java (Apna College) · Google Cloud Bootcamp (GeeksforGeeks) · LeetCode 100 Days Badge 2024</sub>
</p>

<div align="center">

**Open to conversations about backend engineering and distributed systems.** [Say hi →](mailto:vaibhav.jain.careers@gmail.com)

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:8957e5,45:1f6feb,100:0d1117&height=120&section=footer" width="100%"/>

</div>
