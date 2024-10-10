# Domain-Reputation-Check

This project is a Domain Reputation Checker script that allows you to check the reputation of websites or domains. The script takes a list of websites from a file or from direct command-line input, checks the
reputation of each site against a set of preset websites or domains, and also queries popular reputation services to provide additional reputation details.

Features

•	Check website or domain reputation against a preset list.

•	Directly add specific websites for reputation checking via the command line.

•	Perform checks against several online reputation services:

o	APIVoid Domain Reputation (https://www.apivoid.com/tools/domain-reputation-check/)

 o	Spamhaus (https://check.spamhaus.org/)

 o	EasyDMARC (https://easydmarc.com/tools/ip-domain-reputation-check)

o	IPVoid (https://www.ipvoid.com/domain-reputation-check/)

o	Cisco Talos Intelligence (https://talosintelligence.com/reputation_center/)

o	MXToolBox Domain Reputation (https://mxtoolbox.com/domain/)

•	Outputs results with timestamps for easy tracking.

Prerequisites:
Before running this script, ensure you have Python installed. You also need the requests library to handle the HTTP requests.
To install the requests library, run the following command:

    pip install requests

Clone Repository:

    git clone https://github.com/TheDong3r/domain-reputation-checker.git cd domain-reputation-checker

Create a list of websites you want to check (optional) - 
Reminder, that you will need to set your API's with each of the listed websites above. There are rate limits and this will effect your results. 

Use:

    python domain_checker.py websites_file preset_list

- website_files = A text file with the websites/domains you want to check.
- preset_list = A test file with a preset list of potentially unsafe websites/domains (optional).

Example:

    python domain_checker.py websites.txt preset_websites.txt

You can also just search one domain:

Example:

    python domain_checker.py preset_list --sites website1.com website2.org

Output:
The script SHOULD output your results as such:

    YYYY-MM-DD HH:MM:SS - example.com: Safe
    YYYY-MM-DD HH:MM:SS - suspiciousdomain.com: Unsafe


Contributions!

Im new to coding! And trying to learn whereever I can!  Please feel free to contribute to this project by submitting issues or pull requests. Also, if you have
any suggestions for improvement or functionality, I'd love to hear them! Thank you!



    


