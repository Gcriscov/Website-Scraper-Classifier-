
import csv
from parsel import Selector
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# file were scraped profile information will be stored
file_name = 'results_file.csv'
fname = 'linkedIn.txt'
# login credentials
linkedin_username = '' # Change here
linkedin_password = '' # Change here

# function to ensure all key data fields have a value
def validate_field(field):
    # if field is present pass if field:
    if field:
        pass
    # if field is not present print text else:
    else:
        field = 'No results'
    return field


# defining new  variable passing two parameters
writer = csv.writer(open(parameters.file_name, 'w'))

# writerow() method to the write to the file object
writer.writerow(['Name', 'Job Title', 'Company', 'Location', 'URL'])

# specifies the path to the chromedriver.exe
driver = webdriver.Chrome('D:\Instalari\chromedriver_win32\chromedriver')

# driver.get method() will navigate to a page given by the URL address
driver.get('https://www.linkedin.com')

# locate email form by_class_name
username = driver.find_element_by_class_name('login-email')

# send_keys() to simulate key strokes
username.send_keys(parameters.linkedin_username)

# sleep for 0.5 seconds
sleep(0.5)

# locate password form by_class_name
password = driver.find_element_by_class_name('login-password')

# send_keys() to simulate key strokes
password.send_keys(parameters.linkedin_password)
sleep(0.5)

# locate submit button by_xpath
sign_in_button = driver.find_element_by_xpath('//*[@type="submit"]')

# .click() to mimic button click
sign_in_button.click()
sleep(0.5)

with open(fname) as f:
	linkedin_urls = f.readlines();
	# For loop to iterate over each URL in the list returned from the google search query
	for linkedin_url in linkedin_urls:
		linkedin_url = ''.join(linkedin_url);
		# get the profile URL
		driver.get(linkedin_url)
		sleep(5)

		# assigning the source code for the web page to variable sel
		sel = Selector(text=driver.page_source)

		# xpath to extract the text from the class containing the name
		name = sel.xpath('//*[starts-with(@class, "pv-top-card-section__name")]/text()').extract_first()

		# if name exists
		if name:
			# .strip() will remove the new line /n and white spaces
			name = name.strip()

		# xpath to extract the text from the class containing the job title
		job_title = sel.xpath('//*[starts-with(@class, "pv-top-card-section__headline")]/text()').extract_first()

		if job_title:
			job_title = job_title.strip()

		# xpath to extract the text from the class containing the company
		company = sel.xpath('//*[starts-with(@class, "pv-top-card-v2-section__entity-name pv-top-card-v2-section__company-name")]/text()').extract_first()

		if company:
			company = company.strip()

		# xpath to extract the text from the class containing the college
		college = sel.xpath('//*[starts-with(@class, "pv-top-card-v2-section__entity-name pv-top-card-v2-section__school-name")]/text()').extract_first()

		if college:
			college = college.strip()

		# xpath to extract the text from the class containing the location
		location = sel.xpath('//*[starts-with(@class, "pv-top-card-section__location")]/text()').extract_first()

		if location:
			location = location.strip()

		# assignment of the current URL
		linkedin_url = driver.current_url

		# validating if the fields exist on the profile
		name = validate_field(name)
		job_title = validate_field(job_title)
		company = validate_field(company)
		college = validate_field(college)
		location = validate_field(location)
		linkedin_url = validate_field(linkedin_url)

		# printing the output to the terminal
		
		print('\n')
		print(type(linkedin_url))
		print(linkedin_url)
		print('Name: ' + name)
		print('Job Title: ' + job_title)
		print('Company: ' + company)
		print('College: ' + college)
		print('Location: ' + location)
		print('URL: ' + linkedin_url)
		print('\n')

		# writing the corresponding values to the header
		# encoding with utf-8 to ensure all characters get loaded
		writer.writerow([name.encode('utf-8'),
						 job_title.encode('utf-8'),
						 company.encode('utf-8'),
						 college.encode('utf-8'),
						 location.encode('utf-8'),
						 linkedin_url.encode('utf-8')])

# terminates the application
driver.quit()
