from main import Team, Banner

for team in Team.all():
    team.delete()

for banner in Banner.all():
    banner.delete()

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
    t = Team(name=team, key_name=team, enabled=True)
    t.put()
    print 'Team with name \"%s\" created.' %t.name
    

random_banter = [
    '%s fans should better find a new team.',
    'I can\'t understand how %s call themselves a team.',
    'A footbal team? I thought you said %s.',
]

print ''

for team in teams:
    for banter in random_banter:
        b = Banner(
            copy = banter %team,
            team = Team.get_by_key_name(team),
            author_id = 'test@example.com',
            impressions = 1
        )
        b.put()
        print 'New banter banner'
        print 'Banter: %s' %b.copy
        print 'Sent to: %s' %b.team.name
        print 'Impressions left: %i' %b.impressions
        print ''
    print ''