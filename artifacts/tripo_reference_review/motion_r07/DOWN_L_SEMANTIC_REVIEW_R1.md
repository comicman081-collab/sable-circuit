# Independent down_l semantic guide review R1

**HOLD: visible annotation ambiguity.** Reviewer `/root/tripo_intake_review`, Ponytail FULL. Exact requested semantic subject `b66a31f0bc598a3ac77ea90ed1efec1a4f41de63073b223710f3bf0887dd9591d`.

I directly opened the native 1920×1080 `tripo_e_down_l_laterality_r01/ANNOTATED_DOWN_L_1920.png`, SHA `22e12fbba972133eb410cdadd2b9c098a9cb6c201b66ba10efae79df01273d9b`. Blue identifies the actual LEFT supporting leg and orange identifies the RIGHT folded swing leg. The blue sole is near the fixed floor and the orange foot is raised; the pose remains down_l sample 29/frame 9.0625. These are the same lower-body geometry as the original gray frame.

However, the LEFT/BLUE arrow ends at [1031.602,756.857], the projection of the left calf/knee joint hidden behind the orange thigh. In the visible image, its blue dot is on orange material. The RIGHT/ORANGE arrow ends at [1064.784,779.604], also on the orange knee. Consequently the two labels visibly point to the same orange limb region. Numerically correct projection of an occluded joint is insufficient to communicate visible anatomical correspondence to ImageGen. Earlier R4/R5 laterality failures make this distinction material.

The new generator's diff preserves the original bone-weight polygon color mapping and full-cycle camera/fixed-floor sampling. Phase is explicit in inputs and actual capture selection; the semantic gate checks actual phase/frame/sole equality and rejects a borrowed different-phase label. I found no new pose or appearance reconstruction. The sole arrays and gray-body position are not the reason for this HOLD.

Required correction: point the LEFT label to an actually visible blue point, such as the projected left foot/ankle joint near [925.139,950.108], after verifying it is visible in the exact rendered pose. Keep the target derived from actual geometry. Do not invent a pixel position or move a leg to accommodate the label. A fresh image/completion/subject is needed, preserving R1. The RIGHT orange target can remain if it is unambiguous in the new image. No new ImageGen frame should use this ambiguous R1 semantic guide.

Checks: `exact_anatomical_deform_group_mapping` PASS; `unchanged_evaluated_pose_and_fixed_floor` PASS; `native_annotations_match_actual_limbs` HOLD; `geometry_only_no_sable_appearance` PASS. This is a semantic annotation review only; base pose/contact observations are separate. No Blender was launched and no source, annotation, mask or production code was modified by this reviewer.
