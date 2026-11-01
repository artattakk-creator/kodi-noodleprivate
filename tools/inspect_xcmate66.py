"""Pinned .65 and BINGIE evidence; synthetic/read-only Actions inspection."""
import json,xml.etree.ElementTree as E
from pathlib import Path
import inspect_bingie64 as inspect64
import build_bingie60_review as review
previous=review.build
def build(skin,target):
    result=previous(skin,target)
    names=('thumbsborder_focused','DetailsPlot','BingiePlot','Plot')
    definitions=[]
    for file in Path(skin).glob('xml/*.xml'):
        try:root=E.parse(file).getroot()
        except E.ParseError:continue
        for node in root:
            if node.tag=='include' and (node.get('name','') in names or 'FO_Defs' in node.get('name','') or 'DetailsPlot' in node.get('name','')):
                definitions.append(dict(file=file.name,name=node.get('name'),xml=E.tostring(node,encoding='unicode')))
    home=E.parse(Path(skin)/'xml/IncludesHomeBingie.xml').getroot()
    plots=[]
    for node in home.iter('control'):
        if node.get('type')=='textbox':plots.append(E.tostring(node,encoding='unicode'))
    print('BINGIE66_LOCAL_DEFINITIONS '+json.dumps(definitions))
    print('BINGIE66_TEXTBOXES '+json.dumps(plots))
    parents={child:parent for parent in home.iter() for child in parent}
    target66=next(n for n in home.iter('control') if n.get('id')=='90009')
    chain=[]
    while target66 in parents:
        target66=parents[target66]
        chain.append(dict(tag=target66.tag,attrs=target66.attrib,fields=[dict(tag=n.tag,attrs=n.attrib,text=n.text) for n in target66 if n.tag!='control']))
    print('BINGIE66_PLOT_ANCESTORS '+json.dumps(chain))
    return result
review.build=build
inspect64.BASE='5dfc989a6cf71cb61f43b5c3645797e4825b28fc'
inspect64.main()
