# Setup questionnaire - configure the factory once

Answers get written into [template-map](../_shared/template-map.md). Every future run reads that file; no run should ever re-ask them.

1. Which Altium Designer version do you run (the silent template command is claimed only for 25.8.1), and do your older projects come from earlier versions? (noted in `_shared/template-map.md`)
2. Where do your projects live: the root folder or folders of the old projects, and are any of them released or archived? (becomes the projects line in `_shared/template-map.md`)
3. Are the new templates local `.SchDot` files, or Workspace-managed templates? If local, which folder holds them? (becomes the template folder line)
4. Which standard sheet sizes do you use, and which new template file goes with each? (becomes the size table)
5. What are the file names of the old-branding templates? (becomes the old template list)
6. Which title-block parameter names differ between the old and new templates (old name, new name)? (becomes the renames table)
7. How are projects backed up before a run: version control, a copy, or Workspace history? (becomes the backup line)
8. Which parameter action do you want when updating a template? The default is "Add new parameters that exist in the template only". (becomes the parameter action line)
