_aybu_manager_cli() 
{
	local cur prev commands base script
	COMPREPLY=()
	cur="${COMP_WORDS[COMP_CWORD]}"
	prev="${COMP_WORDS[COMP_CWORD-1]}"

	script=$(which aybu_manager_cli)

	case "${prev}" in
	*_info)
		local command results
		command="${prev%_info}_list"
		results=`$script $command 2>/dev/null  | egrep "\*" | cut -d " " -f 3 | tr -d '\n'`
		COMPREPLY=( `compgen -W "${results}" -- ${cur}` )
		return 0
		;;

	*)
		commands=`$script help_commands`
		COMPREPLY=( `compgen -W "${commands}" -- ${cur}` )
		return 0
		;;
	esac
}

complete -F _aybu_manager_cli aybu_manager_cli

