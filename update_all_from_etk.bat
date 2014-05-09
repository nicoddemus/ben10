for /r %i in (update_from_etk*.bat) do (
    pushd %@PATH[%i]
    call update_from_etk.bat
    popd
)
