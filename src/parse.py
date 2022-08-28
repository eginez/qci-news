import requests
from requests import Session
from typing import *
import calendar
from bs4 import BeautifulSoup
import re
import logging
from dataclasses import dataclass
import os


years = [2017, 2018, 2019, 2020, 2021, 2022]
months = [calendar.month_name[i] for i in range(1, 12)]
HOST = "https://elist.ornl.gov/mailman/private/qci-external"


@dataclass
class Section:
    name: str
    start_marker: str
    end_marker: str
    raw_text: Optional[str] = None


all_sections = [
    Section(
        "news",
        "News and Press Releases",
        "Calls for Abstracts and Papers (by due date)",
    ),
    Section(
        "papers",
        "Calls for Abstracts and Papers (by due date)",
        "Select Competitions, Hackathons, and Tutorials (by date)",
    ),
    Section(
        "competitions/tutorials",
        "Select Competitions, Hackathons, and Tutorials (by date)",
        "Select Conferences, Workshops, and Standards (by date)",
    ),
    Section(
        "conferences",
        "Select Conferences, Workshops, and Standards (by date)",
        "Global List of Open Quantum Technology Jobs",
    ),
    Section("jobs new", re.compile("Job Postings \(.+ new\)"), "Job Postings"),
    Section("jobs current", re.compile("Job Postings \(.+ current\)"), "Job Postings"),
    Section(
        "jobs faculty",
        re.compile("Job Postings \(.+ faculty positions\)"),
        "Job Postings",
    ),
    Section(
        "jobs internships",
        re.compile("Job Postings \(.+ internships\)"),
        "Employer Listing",
    ),
]


def find_thread(session: Session, month: str, year: str) -> List[str]:
    url = f"{HOST}/{year}-{month}"
    thread_url = f"{url}/thread.html"
    res = session.get(url)
    html = BeautifulSoup(res.text, "html.parser")
    return [
        f"{url}/{a['href']}" for a in html.find_all("ul")[1].find_all("a", href=True)
    ]


def read_one_bulletin(session: Session, url: str) -> str:
    res = session.get(url)
    job_postings = parse_job_postings(res.text)
    return job_postings

    # jobs location


def parse_job_postings(text: str) -> Set[str]:
    pos = text.find("Job Posting")
    postings = text[pos:].split("\n")[1:]
    companies = set()
    for j in postings:
        try:
            n = re.search(".+ (\(.+\))", j)
            company = n.group(1)
            company = company.replace("(", "").replace(")", "")
            companies.add(company)
        except:
            pass
            # print('ERROR', j)
    return sorted(companies)


def parse_section(txt: str, section: Section) -> str:
    def patt_search(patt, text: str) -> Tuple[int, int]:
        if isinstance(patt, re.Pattern):
            match = re.search(patt, text)
            return match.span()
        else:
            pos = text.find(patt)
            return pos, pos + len(patt)

    _, start = patt_search(section.start_marker, txt)
    end, _ = patt_search(section.end_marker, txt[start:])
    logging.info(start, start + end)

    return txt[start : start + end]


def parse_all_sections(txt: str, sections: List[Section]) -> List[Section]:
    res = []
    for s in sections:
        s.raw_text = parse_section(txt, s)
        res.append(s)
    return res

def load_secrets() -> Tuple[str, str]:
    user=os.getenv("SESSION_USER")
    key=os.getenv("SESSION_KEY")
    return user, key


def main():
    user, key = load_secrets()
    session = requests.Session()
    session.cookies.update({ user: key })
    companies = set()
    for year in years:
        print(f"parsing {year}")
        for m in months:
            bulls = find_thread(session, m, year)
            for b in bulls:
                companies.update(read_one_bulletin(session, b))

    print(sorted(companies))


if __name__ == "__main__":
    main()
