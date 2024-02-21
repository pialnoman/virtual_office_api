import sys

from projects.models import ProjectSharedFiles
from wbs.models import WbsSharedFiles
from wbs.serializers import WbsFileSerializer


def wbs_wise_file_insert(request, wbs_id, upload_by):
    try:

        files = int(request.data.get('total_files')) + 1

        for i in range(1, files):
            indexval = str(i)
            attribute_name = str('file' + indexval)
            file = request.data.get(attribute_name)
            print(attribute_name, file)
            new_wbs_file = WbsSharedFiles.objects.create(wbs_id=wbs_id, file=file, upload_by_id=upload_by)


        return True

    except Exception as e:
        response = 'on line {}'.format(
            sys.exc_info()[-1].tb_lineno), str(e)
        return response


def project_wise_file_insert(work_package_number,request,upload_by):
    try:

        files = int(request.data.get('total_files')) +1

        for i in range(1, files):
            indexval = str(i)
            attribute_name = str('file' + indexval)
            file = request.data.get(attribute_name)
            print(attribute_name,file)
            new_project_file = ProjectSharedFiles.objects.create(work_package_number=work_package_number,file=file, upload_by_id=upload_by)

        return True

    except Exception as e:
        response = 'on line {}'.format(
            sys.exc_info()[-1].tb_lineno), str(e)
        return response

