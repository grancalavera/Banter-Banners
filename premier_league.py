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
    t = Team(name=team, key_name=team)
    t.put()
    print 'Team with name \"%s\" created.' %t.name
    

random_banter = [
    'lorem ipsum dolor sit amet, consectetur adipiscing elit. Nulla sit.',
    'cusce quis eros a massa varius elementum. Mauris adipiscing orci.',
    'cras enim lorem, ornare eget volutpat non, consequat in turpis.',
    'proin eleifend rutrum libero, non tristique enim sollicitudin quis.',
    'integer fermentum vehicula turpis, sagittis sodales lorem bibendum et.',
    'mauris augue libero, mollis ornare laoreet id, interdum sit amet.',
    'suspendisse convallis tellus et tortor egestas fringilla.',
    'mauris placerat ornare interdum. Cras vitae arcu sit amet diam.',
    'duis tempor lacus ac est varius bibendum. Vestibulum elit elit.',
    'vivamus nec diam fringilla augue vulputate facilisis. Nunc ac purus.'
]

print ''

for team in teams:
    for banter in random_banter:
        b = Banner(
            copy = 'The %s team is a %s' %(team, banter),
            team = Team.get_by_key_name(team),
            author_id = 'test@example.com',
            impressions = random.randint(5, 20)
        )
        b.put()
        print 'New banter banner'
        print 'Banter: %s' %b.copy
        print 'Sent to: %s' %b.team.name
        print 'Impressions left: %i' %b.impressions
        print ''
    print ''