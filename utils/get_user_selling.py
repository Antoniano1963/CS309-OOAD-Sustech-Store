def get_user_selling(user_id):
    import user.models
    import commodity.models
    selling_List = commodity.models.Merchandise.objects.filter(upload_user_id__exact=user_id).filter(status__exact=1)
    return_list = []
    for i in selling_List.all():
        return_list.append(i.get_simple_info())
    return return_list