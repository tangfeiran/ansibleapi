from ansibleapi.playbook import PlayBookJob

if __name__ == '__main__':
    PlayBookJob(playbooks=['test.yml'],
                host_list=['172.16.10.54', '172.16.10.53'],
                remote_user='root',
                group_name="test",
                forks=20,
                ext_vars=None,
                passwords='123456'
                )
