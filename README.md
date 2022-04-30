# ticket-behavior-automator
This is the code repository for Emmanuel Lesi's Final Year Project

## links to supporting resources will be provided below

This web application was made as part of Emmanuel Lesi’s final year project.  
Supporting Resources can be found in the links below: 

* [Github Project Code Repository](https://github.com/EmanLesi/ticket-behavior-automator)
* Project Report – link pending
* Project Video – link pending


## Getting Started
To get started Log In or Register a new account by going to the options in the navigation bar.  
Log Out to get to access the registration and login options in the navigation bar.  

## Create Ticket
The 'Create Ticket' button can be found in the navigation bar at the top of the display.  
The title and description of a new ticket can be entered here.  
Submitting a ticket initiates the ticket analysis process to find similar tickets in the system and automatically apply attributes and present solutions for the ticket.

## All Tickets
Selecting the 'ALL Tickets' leads to the ticket index which displays all the tickets in the system.  

### Ticket Content
Each ticket contains:
* An ID
* A Title
* A Description
* Status
* Priority
* Reporter
* Assignee
* Category
* Creation Time
* Updated Time



### Sorting Options
At the top of the ticket index page are a set of sorting option that can query the system to filter out tickets based on a user made set of criteria.  

## Ticket Details
Clicking ticket id on the ticket index page will display the ticket details.  

### Editing Panel
The top of this page is an editing panel that features:  
Dropdown menus to change the ticket status and priority. 
Textboxes to change assignee and category of the ticket, with dropdown options for each textbox containing the users that can be assignees and categories that already exist the system.  
The reporter, ticket title, description, creation time and update time remain constant throughout the life span of a ticket.  


### Ticket Similarities
Below that is the ticket similarities section that displays the top 3 results of the ticket similarity processing.  
Clicking a result will display the ticket details.  
The similarity results can be manually reassessed to account for new tickets that have arrived after the initial assessment by clicking the 'Reassess Similarity'.  
Clicking the 'Apply Recommended Actions and Properties' button will automatically change the attributes of the ticket If there is a common value amongst the summary tickets.  
Any solutions that have been proposed in the similar tickets are displayed in the actions of the ticket.  


### Solution Feedback
If the user viewing the ticket is the reporter of the ticket, they are presented with a solution feedback section that allows them to update the ticket with by notifying the system that the last solution that was proposed was able to resolve the issue.  
This will automatically close the ticket as well as notify other similar tickets of the solution.  
Deeming the last solution as ineffective will change the status to solution ineffective to notify support team that the last solution was not effective.  
If multiple solutions are entered under a ticket, is it is advised that the ineffective solutions are deleted so that the most recent proposed solution is the solution that worked, so that the solution feedback will apply to that solution.  

### Comments
Comments can be added to a ticket to hold a dialogue about the ticket and if a solution is found checking the 'Mark As Solution' checkbox will change the status of the ticket, and label the comment as a potential solution for the user to provide feedback on.  

### Actions
Finally, all actions, comments and solutions are displayed at the bottom and can be removed using the 'Delete Action' button.  

