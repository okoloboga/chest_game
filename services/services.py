# Countig value of comission by referrals count
def comission_counter(user_id: int) -> dict:
    
    comission: int  # result comission by referrals
    user_data = await get_user(session, user_id)
    referrals = user_data.referrals
    
    if referrals < 5:
        comission = 8
    elif 5 <= referrals < 15:
        comission = 7
    elif 15 <= referrals < 30:
        comission = 6
    elif 30 <= referrals < 50:
        comission = 5
    elif 50 <= referrals < 100:
        comission = 4.5
    elif referrals >= 100:
        comission = 3.5
        
    return {'referrals': referrals,
            'comission': comission}       

    