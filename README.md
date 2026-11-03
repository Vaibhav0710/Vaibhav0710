## Hi, I'm Vaibhav

I'm a backend developer at IntelligentDX in Pune, where I build booking and scheduling APIs for eye-care practices on Google Cloud. Day to day that means Python, Node.js and C#/.NET on PostgreSQL. I studied mechanical engineering, then switched to software through PG-DAC at C-DAC (Sunbeam, Pune). In my own time I build distributed systems in Java and Spring Boot.

[Portfolio](https://vaibhavjain-portfolio.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/-vaibhavjain/) · [Resume](https://vaibhavjain-portfolio.vercel.app/Vaibhav_Jain_Java_Backend_Developer_CV.pdf) · vaibhav.jain.careers@gmail.com

### At work

Intern from April 2025, full-time since November 2025.

- **Treatment-plan booking.** An API that books every visit of a multi-appointment plan across up to 15 parallel lanes, with atomic slot reservation and one audit row per appointment. In production since September 2026.
- **Cancel and reschedule.** The EHR we integrate with has no reschedule, so the API books the new slot first, retries at timed offsets and returns HTTP 207 when only part of it succeeds.
- **Background sync.** Cloud Scheduler and Cloud Run Jobs copy schedules for 213 providers, 111 locations and 70 visit types into PostgreSQL, so requests read indexed tables instead of waiting on slow external calls.
- **Faster slot search.** A concurrent pager took slot search from about 2.7–3.6 s to 1.7–2.5 s. I also moved the scheduling APIs to the EHR's FHIR R4 API without changing our API contracts.
- **AI rule generation.** A platform that generates rules with Claude, checks them with validation gates and repairs failures. Prompt caching cut the cost per rule by about 27–31%.
- **Internship.** Moved 10 API read paths across 5 C#/.NET microservices from MongoDB to PostgreSQL in about 8 weeks. 9 reached production with identical responses.

### Projects

**[Voting System](https://github.com/Vaibhav0710/Voting_System)** is an online election platform where tampering with stored votes can be detected. Each vote stores the SHA-256 hash of the vote before it, so editing or deleting a row breaks the chain, and an admin endpoint finds the break. It is six Spring Boot services ([gateway](https://github.com/Vaibhav0710/Voting_Api-Gateway), [user](https://github.com/Vaibhav0710/Voting_User_Service), [candidate](https://github.com/Vaibhav0710/Voting_Candidate_Service), [voting](https://github.com/Vaibhav0710/Voting_Voting_Service), [result](https://github.com/Vaibhav0710/Voting_Result_Service), [eureka](https://github.com/Vaibhav0710/Voting_Eureka_Server)) with Kafka, Redis, PostgreSQL, Resilience4j, Docker and Kubernetes, plus Prometheus, Grafana and Zipkin for monitoring.

- [Courier Management System](https://github.com/Vaibhav0710/Courier-management-system): delivery platform with admin, customer and delivery-partner modules. Spring Boot, MySQL, React.
- [Portfolio](https://github.com/Vaibhav0710/Portfolio): my website. Next.js, TypeScript, Tailwind.
- [Rent-A-Car](https://github.com/Vaibhav0710/Rent_A_Car) and [Pizza Shop](https://github.com/Vaibhav0710/Pizza-Shop): console apps in Java with JDBC and MySQL.
- [User Management API](https://github.com/Vaibhav0710/Backend-Developer-Intern-Assignment-Submission-Details): a CRUD REST API in Node.js and Express, built for an internship assignment.
- [Autonomous Farming Robot](https://github.com/Vaibhav0710/DesignDevelopmentOfAutonomousFarmingWithPlanthealthIndicationSystem): my final-year B.E. project, an ESP32 robot that checks soil and spots leaf disease with OpenCV.

### Recent commits

<!-- recent_commits starts -->
This list fills in after the first daily update.
<!-- recent_commits ends -->

<sub>Updated daily by [a small script](scripts/build_readme.py).</sub>

### Practice

I solve problems on LeetCode and TUF+ and keep the solutions in [Leetcode-solution](https://github.com/Vaibhav0710/Leetcode-solution) and [Daily_DSA](https://github.com/Vaibhav0710/Daily_DSA). I've also worked through [CS50x](https://github.com/Vaibhav0710/CS50X) and [CS50P](https://github.com/Vaibhav0710/CS50P).
