import rules

rules.add_perm('dj.browse', rules.is_authenticated)
rules.add_perm('dj.suggest_song', rules.is_authenticated)
rules.add_perm('dj.vote_song', rules.is_authenticated)
rules.add_perm('dj.validate_song', rules.is_authenticated & rules.is_staff)
rules.add_perm('dj.ban_song', rules.is_authenticated & rules.is_staff)
rules.add_perm('dj.skip_song', rules.is_authenticated & rules.is_staff)
rules.add_perm('dj.set_volume', rules.is_authenticated & rules.is_staff)
