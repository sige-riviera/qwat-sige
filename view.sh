



psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_access_aid.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_benching.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_backflow_prevention.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_channel.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_cover.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -c "$(${DIR}/view/vw_maintenance_examination.py ${PGSERVICE})"
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -c "$(${DIR}/view/vw_damage.py ${PGSERVICE})"
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_discharge_point.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_dryweather_downspout.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_dryweather_flume.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_manhole.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_reach.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_special_structure.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_wastewater_node.sql
# psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_qgep_cover.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -v SRID=$SRID -f ${DIR}/view/vw_qgep_wastewater_structure.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -f ${DIR}/view/vw_qgep_reach.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -c "$(${DIR}/view/vw_oo_overflow.py ${PGSERVICE} ${SRID})"
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -c "$(${DIR}/view/vw_oo_organisation.py ${PGSERVICE})"

psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -v SRID=$SRID -f ${DIR}/view/vw_catchment_area_connections.sql
psql "service=${PGSERVICE}" -v ON_ERROR_STOP=1 -v SRID=$SRID -f ${DIR}/view/vw_change_points.sql
