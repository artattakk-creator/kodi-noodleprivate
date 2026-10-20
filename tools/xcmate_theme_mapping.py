#!/usr/bin/env python3
"""Audited renderer matrix: bound keys, conditional fallbacks and unused slots.

This inventories consumers, not screenshot/rendering acceptance. Every original
is listed, including graphics for capabilities with no existing UI action.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def binding(key):
    if key=='branding.icon': return 'CORE_BUNDLED','src/plugin.video.xtreammate/icon.png; main.ADDON_ICON','Always present, independent of optional theme'
    if key.startswith('background.home.') or key in {'icon.start','icon.live','icon.epg','icon.movies','icon.series','icon.settings'}:
        return 'BOUND','home_menu.show','Focused home category artwork; icon.live also live logo fallback'
    if key.startswith(('background.settings.','icon.settings.')):
        return 'BOUND','home_menu.settings','Only the selected settings category; groups icon also live group rows'
    if key in {'background.home','background.movies','background.series','focus.default','focus.media','focus.rail','panel.default','panel.overlay'}:
        return 'BOUND','main.Router._add_dir; appearance.window_source; theme_render.LIVE_TEXTURES','Current view/control only'
    if key.startswith('placeholder.'):
        return 'CONDITIONAL','media_art.local_art','Provider artwork takes precedence; cached local fallback when absent'
    if key.startswith('widget.'):
        return 'CONDITIONAL','app_routes.add_index_item; media_art.local_art','Widget routes only; provider artwork wins; banner depends on skin widget layout'
    if key.startswith('icon.media.'):
        return 'CONDITIONAL','theme_render.action_art; MediaWindow._fill','Only existing actions; favourite-add/remove follows real state; trailer requires actual trailer'
    if key in {'panel.sidebar','panel.player.infobar','panel.player.controls','panel.player.options','panel.player.progress-track'}:
        return 'BOUND','LiveNavigator._build_controls/_render_transport','Existing native image controls, exact original geometry and input handlers'
    if key.startswith('icon.player.') and key.rsplit('.',1)[1] not in ('skip-back','skip-forward'):
        return 'BOUND','theme_render.LIVE_TEXTURES; LiveNavigator._render_transport','Current transport/settings icon only; seek capability unchanged'
    if key in {'background.epg.guide','background.epg.detail','status.epg.no-data','status.epg.source-error','icon.epg.clock'}:
        return 'CONDITIONAL','theme_render.guide_state; GuideWindow','Guide state and programme focus; status uses actual query result/error'
    if key in {'icon.epg.channels','icon.epg.day-prev','icon.epg.day-next','icon.epg.remind'}:
        return 'CONDITIONAL','theme_render.decorate_xml; GuideWindow.onClick; theme_render.LIVE_TEXTURES','Existing day buttons, programme reminder and channel/group controls'
    if key in {'icon.shared.search','icon.shared.info','icon.shared.back','panel.divider','panel.media.poster.shade','panel.media.rail.gradient'}:
        return 'BOUND','theme_render.decorate_xml','Nonfocusable decoration only; all existing focus rectangles/navigation remain'
    if key in {'icon.shared.check','icon.shared.forward','icon.shared.clear','icon.shared.close'}:
        return 'CONDITIONAL','theme_ui.manage; theme_render.choice_items','Active-theme native design manager icons; same choices, indices and cancellation'
    return 'UNCONNECTED','none','No new action or startup/loading screen fabricated; reserved for reviewed future UI'


def report(repo=ROOT):
    source=Path(repo)/'themes/xcmate/space-premium'
    spec=json.loads((source/'theme.json').read_text())
    keys=[]
    for key,path in spec['assets'].items():
        status,consumer,condition=binding(key)
        keys.append(dict(key=key,path=path,status=status,consumer=consumer,condition=condition))
    for row in keys:
        if row['status']=='UNCONNECTED':
            aliases=[other['key'] for other in keys if other['path']==row['path'] and other['status']!='UNCONNECTED']
            if aliases: row.update(status='ALIAS_ONLY',consumer=', '.join(aliases),condition='Same original image used through another logical key; no direct resolver call')
    files=[]
    for path in spec['required_files']:
        rows=[r for r in keys if r['path']==path]
        files.append(dict(path=path,sha256=spec['sha256'][path],properties=spec['asset_properties'][path],
            keys=[r['key'] for r in rows],consumers=[r['consumer'] for r in rows if r['status']!='UNCONNECTED'],
            runtime_bound=any(r['status']!='UNCONNECTED' for r in rows)))
    return dict(schema_version=1,original_files=len(files),logical_keys=len(keys),
        runtime_bound_files=sum(r['runtime_bound'] for r in files),
        key_status_counts={status:sum(r['status']==status for r in keys) for status in sorted({r['status'] for r in keys})},
        renderer_acceptance='NOT_RUN_ANDROID',not_all_assets_visible_simultaneously=True,
        files=files,keys=keys)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    result=report();Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('files','keys')},indent=2))
