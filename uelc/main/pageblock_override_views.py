from annoying.decorators import render_to
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template.context import RequestContext
from pagetree.models import Section, PageBlock, Hierarchy, Version
from uelc.main.models import PageBlockDT


def edit_pageblock(request, pageblock_id, success_url=None):
    block = get_object_or_404(PageBlockDT, id=pageblock_id)
    section = block.section
    section.save_version(
        request.user,
        activity="edit pageblock [%s]" % unicode(block))
    block.edit(request.POST, request.FILES)
    if success_url is None:
        success_url = section.get_edit_url()
    return HttpResponseRedirect(success_url)

def add_pageblock(request, section_id, success_url=None):
    section = get_object_or_404(Section, id=section_id)
    blocktype = request.POST.get('blocktype', '')
    section.save_version(user=request.user,
                         activity="add pageblock [%s]" % blocktype)
    # now we need to figure out which kind of pageblock to create
    for pb_class in section.available_pageblocks():
        if pb_class.display_name == blocktype:
            # a match
            block = pb_class.create(request)
            neword = section.pageblock_set.count() + 1
            PageBlockDT.objects.create(section=section, 
                                       label=request.POST.get('label', ''),
                                       ordinality=neword,
                                       css_extra=request.POST.get('css_extra', ''),
                                       content_object=block)
    if success_url is None:
        success_url = section.get_edit_url()
    import pdb
    pdb.set_trace()
    return HttpResponseRedirect(success_url)
