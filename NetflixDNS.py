import re, urllib.request, datetime, subprocess
import win32com.shell.shell as shell

def setDNS(intName, dns1='',dns2=''):
    if dns1 == '' and dns2 == '':
        cmd = 'netsh interface ip set dnsservers name=%s dhcp' % intName
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+cmd)

    else:
        cmd = 'netsh interface ip add dnsservers name=%s %s' % (intName, dns1)
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+cmd)
        
    if dns2 != '':
        cmd = 'netsh interface ip add dnsservers name=%s %s index=2' % (intName, dns2)
        shell.ShellExecuteEx(lpVerb='runas', lpFile='cmd.exe', lpParameters='/c '+cmd)

def validDNS(server=''):

    proc = subprocess.Popen('nslookup netflix.com %s' % server, stdout=subprocess.PIPE)
    out, err = proc.communicate()
    return 'netflix.com' in out.decode('utf-8')
        
def getNewDNS(intName):
    ipMatcher = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')

    months = [''
              ,'january'
              ,'february'
              ,'march'
              ,'april'
              ,'may'
              ,'june'
              ,'july'
              ,'august'
              ,'september'
              ,'october'
              ,'november'
              ,'december']

    dateToUse = datetime.date.today()
    currStuff = (dateToUse.replace(day=1)).strftime("%Y-%m").split('-')

    htmlContents = ''
    DNSList = []
    for i in range(12,0,-1):
        
        myUrl = 'http://www.netflixdnscodes.com/dns-codes/american-dns-codes-%s-%s/' % (months[int(currStuff[1])],currStuff[0])
        print('Searching for %s %s.' % (months[int(currStuff[1])].title(),currStuff[0]))
        try:
            urlRequest = urllib.request.Request(myUrl, headers={'User-Agent': 'Mozilla/5.0'})
            htmlContents = urllib.request.urlopen(urlRequest).read().decode('utf-8')
            x = (ipMatcher.findall(htmlContents))
            for e in range(0,len(x),2):
                DNSList.append([x[e],x[e+1]])
            print('Using %s %s.' % (months[int(currStuff[1])].title(),currStuff[0])) 
            break
        except urllib.error.HTTPError:
            print('No records found.')
            dateToUse = dateToUse.replace(day=1) - datetime.timedelta(days=1)
            currStuff = (dateToUse.replace(day=1)).strftime("%Y-%m").split('-')
            continue

    for d in range(0,len(DNSList)):
        dns1 = DNSList[d][0]
        dns2 = DNSList[d][1]
        print('Trying DNS %d / %d.' % (d*2+1, len(DNSList)*2))

        if not validDNS(dns1):
            print('Trying DNS %d / %d.' % (d*2+2, len(DNSList)*2))
            res2 = subprocess.Popen('nslookup 127.0.0.1 %s' % dns2, stdout=subprocess.PIPE)
            out2, err2 = res2.communicate()
            
            if not validDNS(dns2):
                continue
            else:
                #set pref dns to dns2
                print('Using %s.' % dns2)
                setDNS(intName,dns2,'')
                break
                
        else:
            #set pref dns to dns1
            #set alt dns to dns2
            print('Using %s.' % dns1)
            setDNS(intName,dns1,dns2)
            break

print('Welcome to Netflix DNS Manager.\n\nPlease select a network interface.\n')
interfaces = subprocess.Popen('netsh interface show interface', stdout=subprocess.PIPE)
intOut, err = interfaces.communicate()
print(intOut.decode('utf-8'))
workingInterface = input('Enter the interface name exactly as written above: ')
print('\nYou have selected %s.\n\nPlease select an option:' % workingInterface)
print('''
    1. Set a new Netflix DNS.
    2. Test current DNS. **Note this only tells you if the server is online, not whether it changes the Netflix country.**
    3. Reset DNS.
    4. EXIT.''')
choice = '0'
while 1:
    choice = input('\nPlease enter a choice: ')
    if choice == '1':
        getNewDNS(workingInterface)
    elif choice == '2':
        if not validDNS():
            print("\nIt looks like your DNS can't access netflix.com! Try using option 1 to get a new DNS.")
        else:
            print("Your DNS can access netflix.com. If you can't access US shows, try using option 1 again.")
    elif choice == '3':
        dns1 = input('\nEnter a primary DNS server, or leave blank for automatic: ')
        if dns1 == '':
            setDNS(workingInterface)
        else:
            dns2 = input('Enter an alternate DNS server, or leave blank: ')
            setDNS(workingInterface,dns1,dns2)
    elif choice == '4':
        exit()
    else:
        print('Please enter valid input.')
    
                

    
