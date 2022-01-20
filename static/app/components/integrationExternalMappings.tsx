import {Fragment} from 'react';
import styled from '@emotion/styled';
import capitalize from 'lodash/capitalize';

import Access from 'sentry/components/acl/access';
import MenuItemActionLink from 'sentry/components/actions/menuItemActionLink';
import AsyncComponent from 'sentry/components/asyncComponent';
import Button from 'sentry/components/button';
import DropdownLink from 'sentry/components/dropdownLink';
import IntegrationExternalMappingInlineForm from 'sentry/components/integrationExternalMappingInlineForm';
import Pagination from 'sentry/components/pagination';
import {Panel, PanelBody, PanelHeader, PanelItem} from 'sentry/components/panels';
import Tooltip from 'sentry/components/tooltip';
import {IconAdd, IconArrow, IconEllipsis, IconQuestion} from 'sentry/icons';
import {t, tct} from 'sentry/locale';
import PluginIcon from 'sentry/plugins/components/pluginIcon';
import space from 'sentry/styles/space';
import {
  ExternalActorMapping,
  ExternalActorMappingOrSuggestion,
  ExternalActorSuggestion,
  Integration,
  Organization,
} from 'sentry/types';
import {getIntegrationIcon, isExternalActorMapping} from 'sentry/utils/integrationUtil';
import EmptyMessage from 'sentry/views/settings/components/emptyMessage';

type CodeOwnersAssociationMappings = {
  [projectSlug: string]: {
    associations: {
      [externalName: string]: string;
    };
    errors: {
      [errorKey: string]: string;
    };
  };
};

type Props = AsyncComponent['props'] & {
  organization: Organization;
  integration: Integration;
  dataEndpoint: string;
  getBaseFormEndpoint: (mapping: ExternalActorMappingOrSuggestion) => string;
  mappings: ExternalActorMappingOrSuggestion[];
  type: 'team' | 'user';
  onCreate: (mapping?: ExternalActorMappingOrSuggestion) => void;
  onDelete: (mapping: ExternalActorMapping) => void;
  pageLinks?: string;
  sentryNamesMapper: (v: any) => {id: string; name: string}[];
  onResults?: (mapping: ExternalActorMappingOrSuggestion, data: any) => void;
};

type State = AsyncComponent['state'] & {
  associationMappings: CodeOwnersAssociationMappings;
};

class IntegrationExternalMappings extends AsyncComponent<Props, State> {
  getEndpoints(): ReturnType<AsyncComponent['getEndpoints']> {
    const {organization} = this.props;
    return [
      [
        'associationMappings',
        `/organizations/${organization.slug}/codeowners-associations/`,
      ],
    ];
  }

  getUnassociatedMappings(): ExternalActorSuggestion[] {
    const {type} = this.props;
    const {associationMappings} = this.state;
    const errorKey = `missing_external_${type}s`;
    const unassociatedMappings = Object.values(associationMappings).reduce(
      (map, {errors}) => {
        return new Set<string>([...map, ...errors[errorKey]]);
      },
      new Set<string>()
    );
    return Array.from(unassociatedMappings).map(externalName => ({externalName}));
  }

  renderMappingName(mapping: ExternalActorMappingOrSuggestion, hasAccess: boolean) {
    const {
      type,
      getBaseFormEndpoint,
      integration,
      dataEndpoint,
      sentryNamesMapper,
      onResults,
    } = this.props;
    const mappingName = isExternalActorMapping(mapping) ? mapping.sentryName : '';
    return hasAccess ? (
      <IntegrationExternalMappingInlineForm
        type={type}
        integration={integration}
        dataEndpoint={dataEndpoint}
        getBaseFormEndpoint={getBaseFormEndpoint}
        mapping={mapping}
        sentryNamesMapper={sentryNamesMapper}
        onResults={onResults}
      />
    ) : (
      mappingName
    );
  }

  renderMappingOptions(mapping: ExternalActorMappingOrSuggestion, hasAccess: boolean) {
    const {type, onDelete} = this.props;
    return isExternalActorMapping(mapping) ? (
      <Tooltip
        title={t(
          'You must be an organization owner, manager or admin to make changes to an external user mapping.'
        )}
        disabled={hasAccess}
      >
        <DropdownLink
          anchorRight
          customTitle={
            <Button
              borderless
              size="small"
              icon={<IconEllipsisVertical size="sm" />}
              disabled={!hasAccess}
            />
          }
        >
          <MenuItemActionLink
            shouldConfirm
            message={t(`Are you sure you want to remove this external ${type} mapping?`)}
            disabled={!hasAccess}
            onAction={() => onDelete(mapping)}
            title={t(`Delete External ${capitalize(type)}`)}
          >
            <RedText>{t('Delete')}</RedText>
          </MenuItemActionLink>
        </DropdownLink>
      </Tooltip>
    ) : (
      <Tooltip
        title={t(`This ${type} mapping suggestion was generated from a CODEOWNERS file`)}
      >
        <Button borderless size="small" icon={<IconQuestion size="sm" />} disabled />
      </Tooltip>
    );
  }

  renderBody() {
    const {integration, mappings, type, onCreate, pageLinks} = this.props;
    const allMappings = [
      ...this.getUnassociatedMappings(),
      // ,
      ...mappings,
    ];
    return (
      <Fragment>
        <Panel>
          <PanelHeader disablePadding hasButtons>
            <HeaderLayout>
              <ExternalNameColumn header>
                {tct('External [type]', {type})}
              </ExternalNameColumn>
              <ArrowColumn>
                <IconArrow direction="right" size="md" />
              </ArrowColumn>
              <SentryNameColumn>{tct('Sentry [type]', {type})}</SentryNameColumn>
              <Access access={['org:integrations']}>
                {({hasAccess}) => (
                  <ButtonColumn>
                    <Tooltip
                      title={tct(
                        'You must be an organization owner, manager or admin to edit or remove a [type] mapping.',
                        {type}
                      )}
                      disabled={hasAccess}
                    >
                      <AddButton
                        data-test-id="add-mapping-button"
                        onClick={() => onCreate()}
                        size="xsmall"
                        icon={<IconAdd size="xs" isCircled />}
                        disabled={!hasAccess}
                      >
                        {tct('Add [type] Mapping', {type})}
                      </AddButton>
                    </Tooltip>
                  </ButtonColumn>
                )}
              </Access>
            </HeaderLayout>
          </PanelHeader>
          <PanelBody>
            {!mappings.length && (
              <EmptyMessage icon={getIntegrationIcon(integration.provider.key, 'lg')}>
                {tct('Set up External [type] Mappings.', {type: capitalize(type)})}
              </EmptyMessage>
            )}
            {allMappings.map((mapping, index) => (
              <Access access={['org:integrations']} key={index}>
                {({hasAccess}) => (
                  <ConfigPanelItem>
                    <Layout>
                      <ExternalNameColumn>
                        <StyledPluginIcon pluginId={integration.provider.key} size={19} />
                        <span>{mapping.externalName}</span>
                      </ExternalNameColumn>
                      <ArrowColumn>
                        <IconArrow direction="right" size="md" />
                      </ArrowColumn>
                      <SentryNameColumn>
                        {this.renderMappingName(mapping, hasAccess)}
                      </SentryNameColumn>
                      <ButtonColumn>
                        {this.renderMappingOptions(mapping, hasAccess)}
                      </ButtonColumn>
                    </Layout>
                  </ConfigPanelItem>
                )}
              </Access>
            ))}
          </PanelBody>
        </Panel>
        <Pagination pageLinks={pageLinks} />
      </Fragment>
    );
  }
}

export default IntegrationExternalMappings;

const AddButton = styled(Button)`
  text-transform: capitalize;
`;

const Layout = styled('div')`
  display: grid;
  grid-column-gap: ${space(1)};
  padding: ${space(1)};
  width: 100%;
  align-items: center;
  grid-template-columns: 2.5fr 50px 2.5fr 1fr;
  grid-template-areas: 'external-name arrow sentry-name button';
`;

const HeaderLayout = styled(Layout)`
  align-items: center;
  padding: 0 ${space(1)} 0 ${space(2)};
  text-transform: uppercase;
`;

const ConfigPanelItem = styled(PanelItem)`
  padding: 0 ${space(1)};
`;

const IconEllipsisVertical = styled(IconEllipsis)`
  transform: rotate(90deg);
`;

const StyledPluginIcon = styled(PluginIcon)`
  margin-right: ${space(2)};
`;

// Columns below
const Column = styled('span')`
  overflow: hidden;
  overflow-wrap: break-word;
`;

const ExternalNameColumn = styled(Column)<{header?: boolean}>`
  grid-area: external-name;
  display: flex;
  align-items: center;
  font-family: ${p => (p.header ? 'inherit' : p.theme.text.familyMono)};
`;

const ArrowColumn = styled(Column)`
  grid-area: arrow;
`;

const SentryNameColumn = styled(Column)`
  grid-area: sentry-name;
  overflow: visible;
`;

const ButtonColumn = styled(Column)`
  grid-area: button;
  text-align: right;
  overflow: visible;
`;

const RedText = styled('span')`
  color: ${p => p.theme.red300};
`;
