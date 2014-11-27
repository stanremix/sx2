import jpush as jpush

_jpush = jpush.JPush('9370f4f126efb68cb51448d9', '5aa29e3617a58eca440a01a9')

push = _jpush.create_push()
aa = []
aa.append('0013e79cbfc')
aa.append('0416fadd27b')
taa = tuple(aa)
#push.audience = jpush.registration_id('0013e79cbfc', '0416fadd27b')
push.audience = jpush.registration_id(*taa)
push.notification = jpush.notification(ios=jpush.ios(alert='#####JPush power cnvnwnovs', badge=1, sound='default'))
push.message = jpush.message('abcdefg')
push.options = dict(apns_production=False)

push.platform = jpush.platform('ios')
push.send()

