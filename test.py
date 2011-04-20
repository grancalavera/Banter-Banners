from main import Banner, Team
import main

team = Team.get_by_key_name('Birmingham City')
print'Banners for the %s team' %team.name

banner = main.serve_banner_for_team(team)

if banner:
    print banner.copy
else:
    print 'All of the banners for the %s team have run out of impressions' %team.name