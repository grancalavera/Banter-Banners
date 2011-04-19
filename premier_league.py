from main import Team

for team in Team.all():
    team.delete()

teams = [
    'Arsenal',
    'Aston Villa',
    'Birmingham City',
    'Blackburn Rovers',
    'Blackpool',
    'Bolton Wanderers',
    'Chelsea',
    'Everton',
    'Fulham',
    'Liverpool',
    'Manchester City',
    'Manchester United',
    'Newcastle United',
    'Stoke City',
    'Sunderland',
    'Tottenham Hotspur',
    'West Bromwich Albion',
    'West Ham United',
    'Wigan Athletic',
    'Wolverhampton Wanderers',
]

for team in teams:
    t = Team(name=team, key_name=team)
    t.put()
    print 'Team with name \"%s\" created.' %t.name